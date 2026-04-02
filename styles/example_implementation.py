"""
Example implementation of professional theme customization for CogniData.

This file shows how to integrate the professional theme into your app.py
and create a modern, professional-looking interface.

IMPORTANT: This is an EXAMPLE. Adapt these patterns to your actual app structure.
"""

import streamlit as st
from styles.professional_theme import (
    inject_professional_css,
    create_custom_alert,
    get_color,
)


def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="CogniData - Neuropsychological Testing",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_professional_sidebar():
    """Render sidebar with professional styling."""
    with st.sidebar:
        # App logo/title
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem; margin-bottom: 2rem;">
                <p style="font-size: 2rem; margin: 0;">🧠</p>
                <p style="color: {get_color('purple_dark')}; font-weight: bold; font-size: 1.5rem; margin: 0.5rem 0 0 0;">
                    CogniData
                </p>
                <p style="color: {get_color('text_dark')}; font-size: 0.85rem; margin: 0.25rem 0 0 0;">
                    Avaliação Neuropsicológica
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Navigation menu
        st.markdown(
            f"<p style='color: {get_color('purple_dark')}; font-weight: 600; margin-bottom: 1rem;'>Navegação</p>",
            unsafe_allow_html=True,
        )

        # Using radio buttons for navigation (simpler than custom)
        page = st.radio(
            "Seleccione uma página",
            [
                "🏠 Início",
                "👥 Pacientes",
                "🧪 Testes",
                "📊 Dashboard",
                "⚙️ Configuração",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        # User info section (if user is logged in)
        if st.session_state.get("user"):
            st.markdown(
                f"""
                <div style="background-color: {get_color('bg_main')}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="font-size: 0.85rem; color: {get_color('text_dark')}; margin: 0 0 0.5rem 0;">
                        <strong>Utilizador</strong>
                    </p>
                    <p style="color: {get_color('purple_dark')}; margin: 0; font-weight: 600;">
                        {st.session_state.user.username}
                    </p>
                    <p style="font-size: 0.8rem; color: {get_color('text_dark')}; margin: 0.5rem 0 0 0;">
                        {st.session_state.user.role}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Logout button
        logout_col = st.columns(1)[0]
        with logout_col:
            if st.button(
                "🚪 Sair",
                use_container_width=True,
                key="logout_btn",
                help="Terminar sessão",
            ):
                st.session_state.user = None
                st.session_state.authenticated = False
                st.rerun()

        return page


def render_main_content(page: str):
    """Render main content based on selected page."""

    if "Início" in page:
        render_home_page()
    elif "Pacientes" in page:
        render_patients_page()
    elif "Testes" in page:
        render_tests_page()
    elif "Dashboard" in page:
        render_dashboard_page()
    elif "Configuração" in page:
        render_config_page()


def render_home_page():
    """Home page with professional styling."""
    st.title("Bem-vindo ao CogniData")

    # Hero section
    st.markdown(
        f"""
        <div style="background-color: {get_color('white')}; padding: 2rem; border-radius: 12px; 
                    border-left: 4px solid {get_color('purple_vibrant')}; margin-bottom: 2rem;">
            <p style="color: {get_color('purple_dark')}; font-size: 1.3rem; font-weight: 600; margin: 0;">
                Avaliação Neuropsicológica Profissional
            </p>
            <p style="color: {get_color('text_dark')}; line-height: 1.6; margin: 1rem 0 0 0;">
                CogniData é uma plataforma completa para gerenciamento de avaliações neuropsicológicas,
                cálculo de scores normativos e geração de relatórios profissionais.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Features grid
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="card">
                <p style="font-size: 2rem; margin: 0;">👥</p>
                <p style="color: {get_color('purple_dark')}; font-weight: 600; margin: 1rem 0 0.5rem 0;">
                    Gestão de Pacientes
                </p>
                <p style="color: {get_color('text_dark')}; font-size: 0.9rem; line-height: 1.5; margin: 0;">
                    Crie e gerencie perfis de pacientes de forma segura e confidencial.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="card">
                <p style="font-size: 2rem; margin: 0;">🧪</p>
                <p style="color: {get_color('purple_dark')}; font-weight: 600; margin: 1rem 0 0.5rem 0;">
                    Testes Cognitivos
                </p>
                <p style="color: {get_color('text_dark')}; font-size: 0.9rem; line-height: 1.5; margin: 0;">
                    Realize avaliações com cálculo automático de scores normativos.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="card">
                <p style="font-size: 2rem; margin: 0;">📊</p>
                <p style="color: {get_color('purple_dark')}; font-weight: 600; margin: 1rem 0 0.5rem 0;">
                    Relatórios Profissionais
                </p>
                <p style="color: {get_color('text_dark')}; font-size: 0.9rem; line-height: 1.5; margin: 0;">
                    Gere relatórios detalhados e personalizados em PDF.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_patients_page():
    """Patients page with professional styling."""
    st.title("Gestão de Pacientes")

    # Create new patient button
    col1, col2 = st.columns([3, 1]
)
    with col2:
        if st.button("➕ Novo Paciente", use_container_width=True):
            st.session_state.show_new_patient_form = True

    st.divider()

    # Example: Empty state
    if True:  # Would check if no patients exist
        create_custom_alert(
            title="Sem Pacientes Registados",
            message="Nenhum paciente foi registado ainda. Clique em 'Novo Paciente' para começar.",
            alert_type="info",
        )


def render_tests_page():
    """Tests page with professional styling."""
    st.title("Realizar Teste Cognitivo")

    create_custom_alert(
        title="Seleccione um Paciente",
        message="Escolha um paciente da lista para realizar uma avaliação cognitiva.",
        alert_type="info",
    )


def render_dashboard_page():
    """Dashboard page with professional styling."""
    st.title("Dashboard de Avaliações")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        ("👥", "Pacientes", "12"),
        ("🧪", "Testes Realizados", "47"),
        ("📊", "Médias Atualizadas", "8"),
        ("📁", "Relatórios", "23"),
    ]

    for col, (icon, label, value) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(
                f"""
                <div class="card" style="text-align: center;">
                    <p style="font-size: 2rem; margin: 0;">{icon}</p>
                    <p style="color: {get_color('text_dark')}; font-size: 0.85rem; margin: 1rem 0 0.5rem 0;">
                        {label}
                    </p>
                    <p style="color: {get_color('purple_vibrant')}; font-size: 2rem; font-weight: 700; margin: 0;">
                        {value}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_config_page():
    """Configuration page with professional styling."""
    st.title("Configuração")

    st.markdown(
        f"""
        <p style="color: {get_color('purple_dark')}; font-weight: 600; font-size: 1.2rem; margin-bottom: 1rem;">
            Definições da Aplicação
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Settings form
    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Nome da Clínica", "CogniData")
        st.text_input("Email de Contacto", "contacto@cognidata.pt")

    with col2:
        st.selectbox("Idioma", ["Português", "Espanhol", "Inglês"])
        st.selectbox("Tema", ["Profissional (Escuro)", "Profissional (Claro)"])


def main():
    """Main application entry point."""
    # Setup page configuration
    setup_page_config()

    # IMPORTANT: Inject CSS FIRST, before any content
    inject_professional_css()

    # Check if user is authenticated
    if not st.session_state.get("authenticated"):
        # Show login page
        st.title("CogniData - Login")
        create_custom_alert(
            title="Autenticação Necessária",
            message="Faça login para aceder à aplicação.",
            alert_type="info",
        )
        # ... login form code ...
        return

    # Render sidebar and get selected page
    selected_page = render_professional_sidebar()

    # Render main content based on selected page
    render_main_content(selected_page)


if __name__ == "__main__":
    main()
