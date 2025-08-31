import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool

from data_quality_assistant.models.state import DataQualityState, VisualizationData
from data_quality_assistant.models.llm_response import SqlGenerationResponse, AnalysisResponse
from data_quality_assistant.llm.prompts import PromptTemplates

logger = logging.getLogger(__name__)


class DataQualityNodes:
    """Collection of processing nodes for data quality analysis."""
    
    def __init__(self, llm: ChatOpenAI, db: SQLDatabase, data_info: Dict[str, Any]) -> None:
        self.llm = llm
        self.db = db
        self.data_info = data_info
        self.prompts = PromptTemplates()
    
    def generate_sql(self, state: DataQualityState) -> DataQualityState:
        """Generate SQL query from user question."""
        
        if state.error_message:
            return state
        
        prompt = self.prompts.get_sql_generation_prompt()
        
        try:
            structured_llm = self.llm.with_structured_output(SqlGenerationResponse)
            
            response = structured_llm.invoke(
                prompt.format_messages(
                    columns=self.data_info.get('columns', []),
                    dtypes=self.data_info.get('dtypes', {}),
                    question=state.user_question
                )
            )
            
            sql_query = response.sql_query.strip()
            return DataQualityState(
                user_question=state.user_question,
                sql_query=sql_query,
                query_result=state.query_result,
                final_answer=state.final_answer,
                error_message=state.error_message
            )
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return DataQualityState(
                user_question=state.user_question,
                sql_query=state.sql_query,
                query_result=state.query_result,
                final_answer=state.final_answer,
                error_message=f"Error generating SQL query: {str(e)}"
            )
    
    def execute_query(self, state: DataQualityState) -> DataQualityState:
        """Execute SQL query against the database."""
        
        if state.error_message or not self.db:
            return state
        
        try:
            query_tool = QuerySQLDatabaseTool(db=self.db)
            result = query_tool.invoke(state.sql_query)
            return DataQualityState(
                user_question=state.user_question,
                sql_query=state.sql_query,
                query_result=str(result),
                final_answer=state.final_answer,
                error_message=state.error_message
            )
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return DataQualityState(
                user_question=state.user_question,
                sql_query=state.sql_query,
                query_result=state.query_result,
                final_answer=state.final_answer,
                error_message=f"Error executing query: {str(e)}"
            )
    
    def generate_answer(self, state: DataQualityState) -> DataQualityState:
        """Generate analysis from query results."""
        
        if state.error_message:
            return self._handle_error(state)
        
        prompt = self.prompts.get_insights_generation_prompt()
        
        try:
            structured_llm = self.llm.with_structured_output(AnalysisResponse)
            
            response = structured_llm.invoke(
                prompt.format_messages(
                    question=state.user_question,
                    sql_query=state.sql_query,
                    results=state.query_result
                )
            )
            
            return DataQualityState(
                user_question=state.user_question,
                sql_query=state.sql_query,
                query_result=state.query_result,
                final_answer=response.final_answer,
                error_message=state.error_message
            )
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return DataQualityState(
                user_question=state.user_question,
                sql_query=state.sql_query,
                query_result=state.query_result,
                final_answer=state.final_answer,
                error_message=f"Error generating answer: {str(e)}"
            )
    
    def _handle_error(self, state: DataQualityState) -> DataQualityState:
        """Handle processing errors with user-friendly messages."""
        
        error_response = f"""
        I encountered an error while processing your question: "{state.user_question}"
        
        Error: {state.error_message or 'Unknown error'}
        
        Please try rephrasing your question or asking something simpler like:
        - "How many rows are in the data?"
        - "What columns are available?"
        - "Show me the first 5 rows"
        """
        
        return DataQualityState(
            user_question=state.user_question,
            sql_query=state.sql_query,
            query_result=state.query_result,
            final_answer=error_response,
            error_message=state.error_message
        )