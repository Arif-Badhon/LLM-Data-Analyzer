"""System health check page"""
import streamlit as st
from components import render_sidebar
from utils import client

st.set_page_config(page_title="Health Check", page_icon="🏥")
render_sidebar()

st.title("🏥 System Health Check")

if st.button("🔄 Check Backend Status", use_container_width=True):
    with st.spinner("Checking..."):
        health = client.health_check()
        
        if health.get("status") == "healthy":
            st.success("✅ Backend is running and healthy!")
            
            # Display details
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Status", health.get("status", "unknown"))
                st.metric("Service", health.get("service", "unknown"))
            
            with col2:
                st.metric("LLM Model", health.get("llm_model", "unknown"))
                st.metric("Environment", health.get("environment", "unknown"))
            
            st.divider()
            
            # Display full response
            st.subheader("📋 Full Response")
            st.json(health)
        else:
            st.error("❌ Backend is not responding or unhealthy")
            if "detail" in health:
                st.error(f"Details: {health['detail']}")
