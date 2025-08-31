
import os
import logging
import pandas as pd
import sqlite3
from typing import Tuple
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase

from data_quality_assistant.models.state import DataQualityState
from data_quality_assistant.llm.nodes import DataQualityNodes
from data_quality_assistant.llm.workflow import DataQualityWorkflow

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQualityAssistant:
    """AI assistant for analyzing data quality using natural language questions."""
    
    def __init__(self, data_path: str, model_name: str = "gpt-4o-mini") -> None:
        self.db_path = "data_quality.db"
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            max_tokens=2000,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.db, self.data_info = self._setup_database(data_path)
        self.nodes = DataQualityNodes(self.llm, self.db, self.data_info)
        self.workflow = DataQualityWorkflow(self.nodes)
        
        logger.info(f"Assistant initialized with data from: {data_path}")
    
    def _setup_database(self, data_path: str) -> Tuple[SQLDatabase, dict]:
        if data_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(data_path)
        elif data_path.endswith('.csv'):
            df = pd.read_csv(data_path)
        else:
            raise ValueError(f"Unsupported file format: {data_path}")
        
        conn = sqlite3.connect(self.db_path)
        df.to_sql('data_table', conn, if_exists='replace', index=False)
        conn.close()
        
        db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")
        
        data_info = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
        }
        
        logger.info(f"Database setup complete. Data shape: {df.shape}")
        return db, data_info
    
    def ask_question(self, question: str) -> DataQualityState:
        """Ask a question about data quality and get analysis results."""
        initial_state = DataQualityState(user_question=question)
        
        try:
            result = self.workflow.invoke(initial_state)
            
            if isinstance(result, dict):
                result = DataQualityState(**result)
            
            return result
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return DataQualityState(
                user_question=question,
                final_answer=f"An error occurred: {str(e)}",
                error_message=str(e)
            )
