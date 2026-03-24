"""
CogniData - Aplicación Neuropsicológica
Streamlit App para gestión de tests y cálculo de normas NEURONORMA

Modular architecture with authentication and role-based access control.
"""

import streamlit as st

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
        st.header("📋 Navegación")
        page = st.radio(
            "Selecciona una sección:",
            [
                "🏠 Inicio",
                "👥 Pacientes",
                "🧪 Tests",
                "📊 Dashboard",
                "⚙️ Configuración",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")
        render_user_menu()
        st.caption("Versión 0.2.0 - Streamlit")
        st.caption("100% Python - SQLite")

    if page == "🏠 Inicio":
        home.render()
    elif page == "👥 Pacientes":
        patients.render()
    elif page == "🧪 Tests":
        tests.render()
    elif page == "📊 Dashboard":
        dashboard.render()
    elif page == "⚙️ Configuración":
        config.render()


if __name__ == "__main__":
    main()
