
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from data_quality_assistant.models.state import DataQualityState
from data_quality_assistant.llm.nodes import DataQualityNodes


class DataQualityWorkflow:
    """LangGraph workflow for data quality analysis."""
    
    def __init__(self, nodes: DataQualityNodes) -> None:
        self.nodes = nodes
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> CompiledStateGraph:
        """Create the LangGraph workflow with 3-step process."""
        workflow = StateGraph(DataQualityState)
        
        workflow.add_node("generate_sql", self.nodes.generate_sql)
        workflow.add_node("execute_query", self.nodes.execute_query)
        workflow.add_node("generate_answer", self.nodes.generate_answer)
        
        workflow.add_edge(START, "generate_sql")
        workflow.add_edge("generate_sql", "execute_query")
        workflow.add_edge("execute_query", "generate_answer")
        workflow.add_edge("generate_answer", END)

        return workflow.compile()
    
    def invoke(self, initial_state: DataQualityState) -> DataQualityState:
        """Execute the workflow and return results."""
        result = self.workflow.invoke(initial_state)
        
        if isinstance(result, dict):
            return DataQualityState(
                user_question=result.get("user_question", ""),
                sql_query=result.get("sql_query", ""),
                query_result=result.get("query_result", ""),
                final_answer=result.get("final_answer", ""),
                error_message=result.get("error_message")
            )
        return result
