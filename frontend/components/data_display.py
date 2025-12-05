"""Data display utilities"""
import streamlit as st
import pandas as pd


def display_data_preview(data: list, columns: list):
    """Display data preview"""
    if not data:
        st.warning("No data to display")
        return
    
    st.subheader("📋 Data Preview")
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(data)
    
    # Display summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", len(df))
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        st.metric("Memory Usage", f"{df.memory_usage().sum() / 1024:.2f} KB")
    
    st.divider()
    
    # Display data table
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # Display statistics
    st.subheader("📊 Data Statistics")
    st.dataframe(df.describe(), use_container_width=True)


def display_analysis_results(results: dict):
    """Display analysis results"""
    st.subheader("📈 Analysis Results")
    
    if "error" in results:
        st.error(f"Analysis failed: {results['error']}")
        return
    
    # Display results based on type
    if "results" in results:
        st.write(results["results"])
    
    if "summary" in results:
        st.info(f"**Summary:** {results['summary']}")
