
from pydantic import BaseModel, Field


class SqlGenerationResponse(BaseModel):
    sql_query: str = Field(description="Generated SQL query")


class AnalysisResponse(BaseModel):
    final_answer: str = Field(description="Analysis and answer to the user's question")
