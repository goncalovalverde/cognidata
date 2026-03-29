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
        # Custom CSS para mejor apariencia
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        .sidebar-header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 2px solid #1E90FF;
            margin-bottom: 20px;
        }
        .sidebar-header h2 {
            margin: 0;
            color: #1E90FF;
            font-size: 28px;
        }
        .sidebar-header p {
            margin: 5px 0 0 0;
            color: #666;
            font-size: 12px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Logo y título profesional
        st.markdown("""
        <div class="sidebar-header">
            <h2>🧠 CogniData</h2>
            <p>Evaluación Neuropsicológica</p>
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
                "container": {
                    "padding": "0!important",
                    "background-color": "#f8f9fa",
                },
                "icon": {
                    "color": "#1E90FF",
                    "font-size": "18px",
                },
                "nav-link": {
                    "font-size": "15px",
                    "text-align": "left",
                    "margin": "0px",
                    "padding": "12px 15px",
                    "--hover-color": "#e6f2ff",
                    "color": "#333333",
                    "border-radius": "0px",
                },
                "nav-link-selected": {
                    "background-color": "#1E90FF",
                    "color": "#ffffff",
                    "font-weight": "600",
                    "border-radius": "0px",
                },
            },
        )

        st.markdown("---")
        render_user_menu()
        
        # Footer con información
        st.markdown("""
        <div style="font-size: 11px; color: #999; text-align: center; margin-top: 30px;">
            <p>v0.2.0 • Streamlit</p>
            <p>100% Python • SQLite</p>
        </div>
        """, unsafe_allow_html=True)

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
