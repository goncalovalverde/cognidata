"""
CogniData - Aplicación Neuropsicológica
Streamlit App para gestión de tests y cálculo de normas NEURONORMA

Modular architecture with authentication and role-based access control.
"""

import streamlit as st
from streamlit_option_menu import option_menu

from database.connection import init_db
from utils.auth import require_auth, render_user_menu, init_auth_state
from app_pages import home, patients, tests, dashboard, config


st.set_page_config(
    page_title="CogniData - Aplicación Neuropsicológica",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
init_auth_state()


def main():
    """Main application entry point"""
    require_auth()

    with st.sidebar:
        # Logo y título
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2>🧠 CogniData</h2>
            <p style="font-size: 12px; color: #666;">Sistema Neuropsicológico</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Menu de navegación moderno
        page = option_menu(
            menu_title="📋 Navegación",
            options=["Inicio", "Pacientes", "Tests", "Dashboard", "Configuración"],
            icons=["house-fill", "people-fill", "clipboard-data", "graph-up", "gear-fill"],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "#1E90FF", "font-size": "18px"},
                "nav-link": {
                    "font-size": "15px",
                    "text-align": "left",
                    "margin": "0px",
                    "padding": "12px 15px",
                    "--hover-color": "#e6f2ff",
                    "color": "#333333",
                },
                "nav-link-selected": {
                    "background-color": "#1E90FF",
                    "color": "#ffffff",
                    "font-weight": "600",
                },
            },
        )

        st.markdown("---")
        render_user_menu()
        st.caption("Versión 0.2.0 - Streamlit")
        st.caption("100% Python - SQLite")

    if page == "Inicio":
        home.render()
    elif page == "Pacientes":
        patients.render()
    elif page == "Tests":
        tests.render()
    elif page == "Dashboard":
        dashboard.render()
    elif page == "Configuración":
        config.render()


if __name__ == "__main__":
    main()
