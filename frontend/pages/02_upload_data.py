"""File upload and preview page"""
import streamlit as st
from components import render_sidebar, display_data_preview
from utils import client

st.set_page_config(page_title="Upload Data", page_icon="📁")
render_sidebar()

st.title("📁 Upload & Preview Data")

st.subheader("Upload File")
uploaded_file = st.file_uploader(
    "Choose a file (CSV or Excel)",
    type=["csv", "xlsx", "xls"],
    help="Upload your data file for analysis"
)

if uploaded_file:
    with st.spinner("📤 Uploading file..."):
        file_bytes = uploaded_file.read()
        result = client.upload_file(file_bytes, uploaded_file.name)
        
        if "error" in result:
            st.error(f"Upload failed: {result['error']}")
        else:
            st.success(f"✅ File uploaded: {result['filename']}")
            
            # Store data in session state
            st.session_state.uploaded_data = result.get("preview", [])
            st.session_state.all_columns = result.get("column_names", [])
            
            # Display file info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", result.get("rows", 0))
            with col2:
                st.metric("Columns", result.get("columns", 0))
            with col3:
                st.metric("File Type", result.get("file_type", "unknown").upper())
            
            st.divider()
            
            # Display preview
            display_data_preview(result.get("preview", []), result.get("column_names", []))
