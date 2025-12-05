"""Helper functions"""
import streamlit as st
from datetime import datetime


def format_timestamp(ts: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ts


def get_analysis_types() -> list:
    """Get available analysis types"""
    return [
        "statistical_summary",
        "trend_detection",
        "outlier_detection",
        "correlation_analysis"
    ]


def display_error(error_msg: str):
    """Display error message"""
    st.error(f"❌ Error: {error_msg}")


def display_success(success_msg: str):
    """Display success message"""
    st.success(f"✅ {success_msg}")


def display_info(info_msg: str):
    """Display info message"""
    st.info(f"ℹ️ {info_msg}")
