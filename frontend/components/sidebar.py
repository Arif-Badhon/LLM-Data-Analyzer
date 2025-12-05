"""Sidebar navigation"""
import streamlit as st
from utils import client


def render_sidebar():
    """Render sidebar with navigation and status"""
    with st.sidebar:
        st.title("🤖 LLM Data Analyzer")
        
        st.divider()
        
        # Backend Status
        st.subheader("Backend Status")
        if st.button("🔄 Check Status"):
            with st.spinner("Checking..."):
                health = client.health_check()
                if health.get("status") == "healthy":
                    st.success(f"✅ Connected - {health.get('llm_model')}")
                else:
                    st.error("❌ Backend not responding")
        
        st.divider()
        
        # Settings
        st.subheader("Settings")
        backend_url = st.text_input(
            "Backend URL",
            value="http://localhost:8000",
            help="Change if backend is running elsewhere"
        )
        
        st.divider()
        
        # About
        st.subheader("About")
        st.caption("LLM Data Analyzer Frontend")
        st.caption("Built with Streamlit & FastAPI")
