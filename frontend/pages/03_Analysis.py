"""Data analysis page"""
import streamlit as st
from components import render_sidebar, display_analysis_results
from utils import client, get_analysis_types

st.set_page_config(page_title="Analysis", page_icon="📊")
render_sidebar()

st.title("📊 Data Analysis")

if "uploaded_data" not in st.session_state or not st.session_state.uploaded_data:
    st.warning("⚠️ Please upload data first on the 'Upload Data' page")
    st.stop()

data = st.session_state.uploaded_data
columns = st.session_state.get("all_columns", [])

st.subheader("Analysis Settings")

col1, col2 = st.columns(2)
with col1:
    analysis_type = st.selectbox(
        "Analysis Type",
        get_analysis_types(),
        help="Choose the type of analysis to perform"
    )

with col2:
    selected_columns = st.multiselect(
        "Columns to Analyze",
        columns,
        default=columns[:3] if len(columns) > 3 else columns,
        help="Select which columns to analyze"
    )

st.divider()

if st.button("🔍 Run Analysis", use_container_width=True):
    with st.spinner("📊 Analyzing data..."):
        result = client.analyze(data, analysis_type, selected_columns)
        
        if "error" in result:
            st.error(f"Analysis failed: {result['error']}")
        else:
            display_analysis_results(result)
            
            # Show suggestions
            if st.checkbox("💡 Get AI Suggestions"):
                with st.spinner("🤖 Generating suggestions..."):
                    suggestions = client.get_suggestions(data, f"Analysis type: {analysis_type}")
                    if "suggestions" in suggestions:
                        st.subheader("💡 Suggestions")
                        for i, suggestion in enumerate(suggestions["suggestions"], 1):
                            st.write(f"{i}. {suggestion}")
