from langchain_core.prompts import ChatPromptTemplate


class PromptTemplates:
 
    @staticmethod
    def get_sql_generation_prompt() -> ChatPromptTemplate:
        """Create prompt template for SQL query generation."""
        system_prompt = """
        You are a SQL expert. Generate a SQLite query to answer the user's question about the data.
        
        Table name: data_table
        Available columns: {columns}
        Data types: {dtypes}
        
        User question: {question}
        
        Generate a SQL query that will answer the question.
        You must respond with a JSON object containing the SQL query.
        
        Example response format:
        {{
            "sql_query": "SELECT COUNT(*) FROM data_table;"
        }}
        
        Important: Return ONLY valid SQL queries without any markdown formatting or explanations.
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Generate the SQL query in the specified JSON format:")
        ])
    
    @staticmethod
    def get_insights_generation_prompt() -> ChatPromptTemplate:
        """Create prompt template for analysis generation."""
        system_prompt = """
        You are a data analyst. Based on the user's question and the SQL query results, provide a direct and concise answer.
        
        User Question: {question}
        SQL Query: {sql_query}
        Query Results: {results}
        
        Provide a straightforward answer that directly addresses the user's question.
        Focus on the facts from the query results. Keep your response concise and to the point.
        Do not include sections like "Key Insights", "Impact on Analysis", or "Actionable Recommendations".
        Simply state what the data shows in response to the question.
        
        You must respond with a JSON object containing your analysis.
        
        Example response format:
        {{
            "final_answer": "Based on the query results, [direct answer to the question]..."
        }}
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Provide your direct answer in the specified JSON format:")
        ])
