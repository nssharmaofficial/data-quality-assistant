"""Streamlit UI for AI-Powered Data Quality Assistant."""

import sys
import os
import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OPENAI_API_KEY not found in environment variables. Please check your .env file.")
    st.info("Make sure you have a .env file in the solution directory with: OPENAI_API_KEY=your_key_here")

sys.path.append('src')

from data_quality_assistant.assistant import DataQualityAssistant
from data_quality_assistant.models.state import DataQualityState


st.set_page_config(
    page_title="AI Data Quality Assistant",
    layout="centered"
)


st.markdown("""
<style>
/* Main container styling */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1000px;
}

/* Chat bubble styling */
.user-message {
    background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 6px 18px;
    margin: 8px 0 8px auto;
    max-width: 75%;
    font-size: 14px;
    text-align: right;
    box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
    position: relative;
    word-wrap: break-word;
}

.user-message::before {
    content: '';
    position: absolute;
    bottom: -2px;
    right: 8px;
    width: 0;
    height: 0;
    border: 6px solid transparent;
    border-top-color: #0056b3;
    border-right: 0;
    margin-left: -6px;
}

.assistant-message {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #2c3e50;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 6px;
    margin: 8px auto 8px 0;
    max-width: 75%;
    font-size: 14px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #dee2e6;
    position: relative;
    word-wrap: break-word;
}

.assistant-message::before {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 8px;
    width: 0;
    height: 0;
    border: 6px solid transparent;
    border-top-color: #e9ecef;
    border-left: 0;
    margin-right: -6px;
}

/* SQL query styling */
.sql-query {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 8px;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    margin: 8px 0;
    overflow-x: auto;
}

/* Compact metrics */
.metric-container {
    background-color: #f8f9fa;
    padding: 8px 12px;
    border-radius: 8px;
    text-align: center;
    border: 1px solid #e9ecef;
}

.metric-value {
    font-size: 18px;
    font-weight: bold;
    color: #007bff;
    margin: 0;
}

.metric-label {
    font-size: 12px;
    color: #666;
    margin: 0;
}

/* Compact headers */
h1 {
    font-size: 24px !important;
    margin-bottom: 0.5rem !important;
}

h2, h3 {
    font-size: 18px !important;
    margin: 1rem 0 0.5rem 0 !important;
}

/* Compact dataframe */
.stDataFrame {
    font-size: 12px;
}

/* Sidebar styling */
.css-1d391kg {
    padding-top: 1rem;
}

/* Input styling */
.stTextInput > div > div > input {
    font-size: 14px;
}

/* Button styling */
.stButton > button {
    font-size: 14px;
    padding: 0.25rem 0.75rem;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'query_results' not in st.session_state:
        st.session_state.query_results = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def load_data_assistant(data_path: str) -> DataQualityAssistant:
    """Load the data quality assistant."""
    try:
        assistant = DataQualityAssistant(data_path)
        return assistant
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None



def execute_query_for_preview(sql_query: str) -> pd.DataFrame:
    """Execute SQL query for preview."""
    try:
        conn = sqlite3.connect('data_quality.db')
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return pd.DataFrame()

def main():
    initialize_session_state()
    
    # Sidebar for original data and overview
    with st.sidebar:
        st.header("Data Overview")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload data file", 
            type=['csv', 'xlsx', 'xls'],
            help="CSV or Excel file"
        )
        
        # Load demo data if no file uploaded
        if uploaded_file is None:
            demo_path = "data/data.xlsx"
            if os.path.exists(demo_path):
                if st.button("Use Demo Data", use_container_width=True):
                    with st.spinner("Loading..."):
                        st.session_state.assistant = load_data_assistant(demo_path)
                        st.session_state.data = pd.read_excel(demo_path)
                        if st.session_state.assistant:
                            st.success("Demo data loaded!")
                            st.rerun()
        
        # Process uploaded file
        if uploaded_file is not None:
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.session_state.assistant is None:
                with st.spinner("Loading..."):
                    st.session_state.assistant = load_data_assistant(temp_path)
                    if st.session_state.assistant:
                        if temp_path.endswith(('.xlsx', '.xls')):
                            st.session_state.data = pd.read_excel(temp_path)
                        else:
                            st.session_state.data = pd.read_csv(temp_path)
                        st.success("Data loaded!")
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        # Show data overview if data is loaded
        if st.session_state.data is not None:
            # Compact metrics
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{st.session_state.data.shape[0]:,}</div>
                    <div class="metric-label">Rows</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{st.session_state.data.shape[1]}</div>
                    <div class="metric-label">Columns</div>
                </div>
                """, unsafe_allow_html=True)
            
            missing_count = st.session_state.data.isnull().sum().sum()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{missing_count:,}</div>
                <div class="metric-label">Missing Values</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("Original Data")
            st.dataframe(st.session_state.data.head(15), height=300, use_container_width=True)
    
    # Main chat interface
    st.title("AI Data Quality Assistant")
    
    if st.session_state.assistant is None:
        st.info("Please upload a data file or use demo data to get started!")
        return
    
    st.markdown("Ask questions about your data in natural language!")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, (question, answer, query_result) in enumerate(st.session_state.chat_history):
            # User message
            st.markdown(f'<div class="user-message">{question}</div>', unsafe_allow_html=True)
            
            # Assistant message
            st.markdown(f'<div class="assistant-message">{answer}</div>', unsafe_allow_html=True)
            
            # Show SQL query if available
            if query_result and query_result.sql_query and not query_result.error_message:
                with st.expander("View SQL Query", expanded=False):
                    st.markdown(f'<div class="sql-query">{query_result.sql_query}</div>', unsafe_allow_html=True)
            
            # Show query results
            if query_result and query_result.sql_query and not query_result.error_message:
                with st.expander("Query Results", expanded=False):
                    try:
                        query_df = execute_query_for_preview(query_result.sql_query)
                        if not query_df.empty:
                            st.dataframe(query_df, height=200, use_container_width=True)
                        else:
                            st.info("Query returned no results")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            st.markdown("---")
    
    # Question input at the bottom
    with st.form("question_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_question = st.text_input("", placeholder="e.g., How many missing values are there?", label_visibility="collapsed")
        with col2:
            ask_button = st.form_submit_button("Ask", use_container_width=True)
    
    # Process new question
    if ask_button and user_question:
        with st.spinner("Analyzing your question..."):
            result = st.session_state.assistant.ask_question(user_question)
            # Add to chat history
            st.session_state.chat_history.append((user_question, result.final_answer, result))
        st.rerun()
    


if __name__ == "__main__":
    main()
