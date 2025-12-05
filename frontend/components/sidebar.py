"""Sidebar navigation"""
import streamlit as st
from utils import client


def render_sidebar():
    """Render sidebar with navigation and status"""
    with st.sidebar:
        st.title("🤖 LLM Data Analyzer")
        
        st.divider()
        
        # Navigation
        st.subheader("Navigation")
        
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")
        
        if st.button("💬 Chat", use_container_width=True):
            st.switch_page("pages/01_Chat.py")
        
        if st.button("📁 Upload Data", use_container_width=True):
            st.switch_page("pages/02_Upload_Data.py")
        
        if st.button("📊 Analysis", use_container_width=True):
            st.switch_page("pages/03_Analysis.py")
        
        if st.button("🏥 Health Check", use_container_width=True):
            st.switch_page("pages/04_Health_Check.py")
        
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
