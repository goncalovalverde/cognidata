"""
Modal alert system for consistent, professional alerts throughout the application
"""

import streamlit as st
from utils.colors import COLORS


def modal_success(message: str, title: str = "✅ Éxito"):
    """Show success modal alert"""
    @st.dialog(title, width="large")
    def show_modal():
        st.markdown(f"""
        <div style='
            background-color: {COLORS['success']}20;
            border-left: 4px solid {COLORS['success']};
            padding: 16px;
            border-radius: 6px;
            color: {COLORS['text_dark']};
            font-size: 16px;
        '>
            {message}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Cerrar", key=f"success_{title}", type="primary", use_container_width=True):
                pass
    
    show_modal()


def modal_error(message: str, title: str = "❌ Error"):
    """Show error modal alert"""
    @st.dialog(title, width="large")
    def show_modal():
        st.markdown(f"""
        <div style='
            background-color: {COLORS['danger']}20;
            border-left: 4px solid {COLORS['danger']};
            padding: 16px;
            border-radius: 6px;
            color: {COLORS['text_dark']};
            font-size: 16px;
        '>
            {message}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Cerrar", key=f"error_{title}", type="primary", use_container_width=True):
                pass
    
    show_modal()


def modal_warning(message: str, title: str = "⚠️ Advertencia"):
    """Show warning modal alert"""
    @st.dialog(title, width="large")
    def show_modal():
        st.markdown(f"""
        <div style='
            background-color: {COLORS['warning']}20;
            border-left: 4px solid {COLORS['warning']};
            padding: 16px;
            border-radius: 6px;
            color: {COLORS['text_dark']};
            font-size: 16px;
        '>
            {message}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Entendido", key=f"warning_{title}", type="primary", use_container_width=True):
                pass
    
    show_modal()


def modal_info(message: str, title: str = "ℹ️ Información"):
    """Show info modal alert"""
    @st.dialog(title, width="large")
    def show_modal():
        st.markdown(f"""
        <div style='
            background-color: {COLORS['info']}20;
            border-left: 4px solid {COLORS['info']};
            padding: 16px;
            border-radius: 6px;
            color: {COLORS['text_dark']};
            font-size: 16px;
        '>
            {message}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("De acuerdo", key=f"info_{title}", type="primary", use_container_width=True):
                pass
    
    show_modal()


# Inline alert functions (non-modal, for notifications that don't block)
def toast_success(message: str):
    """Show success toast notification"""
    st.success(message)


def toast_error(message: str):
    """Show error toast notification"""
    st.error(message)


def toast_warning(message: str):
    """Show warning toast notification"""
    st.warning(message)


def toast_info(message: str):
    """Show info toast notification"""
    st.info(message)
