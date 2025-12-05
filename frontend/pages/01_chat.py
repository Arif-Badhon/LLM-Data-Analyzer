"""Chat page"""
import streamlit as st
from components import render_sidebar, render_chat

st.set_page_config(page_title="Chat", page_icon="💬")
render_sidebar()
render_chat()
