"""Main Streamlit app"""
import streamlit as st
from components import render_sidebar
from utils import PAGE_TITLE, PAGE_ICON

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar()

st.title("🤖 LLM Data Analyzer")
st.subtitle("Advanced data analysis with AI assistance")

st.divider()

# Home page content
col1, col2 = st.columns(2)

with col1:
    st.subheader("💬 Chat")
    st.write("""
    - Ask questions about data analysis
    - Get AI-powered insights
    - Real-time responses from LLM
    """)
    st.page_link("pages/01_Chat.py", label="Go to Chat", icon="💬")

with col2:
    st.subheader("📁 Upload Data")
    st.write("""
    - Upload CSV or Excel files
    - Preview your data
    - View statistics
    """)
    st.page_link("pages/02_Upload_Data.py", label="Upload Data", icon="📁")

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("📊 Analysis")
    st.write("""
    - Statistical analysis
    - Trend detection
    - Outlier detection
    - Correlation analysis
    """)
    st.page_link("pages/03_Analysis.py", label="Run Analysis", icon="📊")

with col4:
    st.subheader("🏥 System Status")
    st.write("""
    - Check backend health
    - View LLM model info
    - Monitor system status
    """)
    st.page_link("pages/04_Health_Check.py", label="Check Status", icon="🏥")

st.divider()

st.info("""
### 📖 Quick Start
1. **Upload Data** - Start by uploading a CSV or Excel file
2. **Preview** - Review your data and statistics
3. **Analyze** - Run analysis and get insights
4. **Chat** - Ask follow-up questions to the AI
""")
