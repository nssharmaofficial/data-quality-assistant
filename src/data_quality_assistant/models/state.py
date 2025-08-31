from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class VisualizationData(BaseModel):
    type: str = Field(description="Type of visualization")
    data: Dict[str, Any] = Field(description="Visualization data")
    title: str = Field(description="Visualization title")


class DataQualityState(BaseModel):
    user_question: str = Field(default="", description="User's question")
    sql_query: str = Field(default="", description="Generated SQL query")
    query_result: str = Field(default="", description="Query result")
    final_answer: str = Field(default="", description="AI-generated answer")
    error_message: Optional[str] = Field(default=None, description="Error message")
