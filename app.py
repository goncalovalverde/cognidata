"""
CogniData - Aplicación Neuropsicológica
Streamlit App para gestión de tests y cálculo de normas NEURONORMA

Modular architecture with authentication and role-based access control.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env.local (if it exists)
# This must be done BEFORE any other imports that use os.getenv()
load_dotenv('.env.local')

import streamlit as st
from streamlit_option_menu import option_menu

from database.connection import init_db
from utils.auth import require_auth_with_persistence, render_user_menu, init_auth_state
from utils.colors import COLORS
from app_pages import home, patients, tests, dashboard, config, protocols
from components.design_components import apply_design_system
from components.logo_header import render_logo_header
from styles.professional_theme import inject_professional_css


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
    # CRITICAL: Inject professional CSS theme FIRST, before any st operations
    inject_professional_css()
    
    # Apply Triune design system (colors, typography, icons)
    apply_design_system()
    
    require_auth_with_persistence()  # NEW: With session persistence via JWT cookies

    with st.sidebar:
        # Render professional logo header with brain illustration
        render_logo_header()
        
        # Menú de navegación con colores profesionales
        page = option_menu(
            menu_title="📋 Navegación",
            options=["Inicio", "Pacientes", "Tests", "Protocolos", "Dashboard", "Configuración"],
            icons=["house-fill", "people-fill", "clipboard-data", "bookmark-fill", "graph-up", "gear-fill"],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {
                    "padding": "0!important",
                    "background-color": COLORS['background'],
                },
                "icon": {
                    "color": COLORS['secondary'],
                    "font-size": "18px",
                },
                "nav-link": {
                    "font-size": "15px",
                    "text-align": "left",
                    "margin": "0px",
                    "padding": "12px 15px",
                    "--hover-color": f"{COLORS['primary_light']}22",  # Verde claro transparente
                    "color": COLORS['text_dark'],
                    "border-radius": "0px",
                },
                "nav-link-selected": {
                    "background-color": COLORS['primary'],
                    "color": "#ffffff",
                    "font-weight": "600",
                    "border-radius": "0px",
                    "border-left": f"4px solid {COLORS['primary_dark']}",
                },
            },
        )

        st.markdown("---")
        render_user_menu()
        
        # Footer
        st.markdown(f"""
        <div style="font-size: 11px; color: {COLORS['text_light']}; text-align: center; margin-top: 30px;">
            <p>v0.2.0 • Streamlit</p>
            <p>100% Python • SQLite</p>
        </div>
        """, unsafe_allow_html=True)

    # Page routing
    if page == "Inicio":
        home.render()
    elif page == "Pacientes":
        patients.render()
    elif page == "Tests":
        tests.render()
    elif page == "Protocolos":
        protocols.render()
    elif page == "Dashboard":
        dashboard.render()
    elif page == "Configuración":
        config.render()


if __name__ == "__main__":
    main()
