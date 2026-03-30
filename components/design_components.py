"""
CogniData Design System - Streamlit Components
Componentes reutilizables siguiendo la estética Triune
"""

import streamlit as st
from typing import Optional, Literal

# ============================================================================
# CUSTOM CSS STREAMLIT
# ============================================================================

def apply_design_system():
    """
    Aplica el design system de Triune a toda la aplicación Streamlit.
    Debe ejecutarse una sola vez al inicio de la app.
    """
    # Import Phosphor Icons library
    phosphor_icons_html = """
    <link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    """
    
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Montserrat:wght@400;500;600&display=swap');
    
    :root {
        --color-primary-900: #451A4D;
        --color-primary-800: #6B2E6F;
        --color-primary-700: #8D3FCA;
        --color-primary-600: #A942EA;
        --color-primary-500: #B867F0;
        --color-accent-700: #B8860B;
        --color-accent-600: #DAA520;
        --color-accent-500: #F0D958;
        --color-accent-100: #FEF9E7;
        --color-gray-50: #F8F9FA;
        --color-gray-100: #F6F5F2;
        --color-gray-200: #EEEBE5;
        --color-gray-300: #E0DCD5;
        --color-gray-400: #C9C4BB;
        --color-gray-600: #75687F;
        --color-gray-700: #5F577A;
        --color-gray-900: #1F2937;
        --color-gray-950: #111827;
        --color-success-500: #10B981;
        --color-success-100: #ECFDF5;
        --color-error-500: #EF4444;
        --color-error-100: #FEE2E2;
        --color-warning-500: #F59E0B;
        --color-warning-100: #FFFBEB;
        --color-info-500: #3B82F6;
        --color-info-100: #EFF6FF;
    }

    /* BODY */
    body {
        font-family: "Montserrat", "Open Sans", sans-serif;
        background-color: var(--color-gray-50);
        color: var(--color-gray-700);
    }

    /* TÍTULOS */
    h1, h2, h3, h4, h5, h6 {
        font-family: "Playfair Display", Georgia, serif;
        color: var(--color-primary-900);
        letter-spacing: -0.01em;
    }

    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }

    h2 {
        font-size: 1.875rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    h3 {
        font-size: 1.25rem;
        font-weight: 600;
    }

    /* BOTONES STREAMLIT */
    .stButton > button {
        background-color: var(--color-primary-600);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        font-family: "Montserrat", sans-serif;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background-color: var(--color-primary-700);
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.15);
    }

    .stButton > button:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.2);
    }

    /* INPUTS STREAMLIT */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 1px solid var(--color-gray-200) !important;
        border-radius: 6px !important;
        font-family: "Montserrat", sans-serif !important;
        color: var(--color-gray-700) !important;
        font-size: 1rem !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus,
    .stTimeInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--color-primary-600) !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
    }

    /* LABELS */
    .stLabel > label {
        font-family: "Montserrat", sans-serif;
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--color-gray-900);
    }

    /* SELECTBOX */
    .stSelectbox > div > div > div {
        border-radius: 6px !important;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] button {
        border-radius: 6px 6px 0 0 !important;
        font-family: "Montserrat", sans-serif !important;
        font-weight: 600 !important;
        color: var(--color-gray-700) !important;
    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: var(--color-primary-600) !important;
        color: white !important;
    }

    /* EXPANDABLE */
    .streamlit-expanderHeader {
        background-color: var(--color-gray-100) !important;
        border-radius: 6px !important;
        font-family: "Montserrat", sans-serif !important;
        font-weight: 600 !important;
    }

    .streamlit-expanderHeader:hover {
        background-color: var(--color-gray-200) !important;
    }

    /* SCROLL */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--color-gray-100);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--color-gray-400);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-gray-600);
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # Inject Phosphor Icons library
    st.markdown(phosphor_icons_html, unsafe_allow_html=True)


# ============================================================================
# COMPONENTES PERSONALIZADOS
# ============================================================================

def header(title: str, subtitle: str = "", icon: str = ""):
    """
    Encabezado profesional con estilo Triune.
    
    Args:
        title: Título principal
        subtitle: Subtítulo (opcional)
        icon: Emoji o icon (opcional)
    """
    title_html = f'{icon} {title}' if icon else title
    subtitle_html = f'<p style="font-size: 1.1rem; color: #75687F; margin: 0;">{subtitle}</p>' if subtitle else ''
    html = f'<div style="margin-bottom: 2rem;"><h1 style="font-family: \'Playfair Display\', serif; font-size: 2.5rem; font-weight: 700; color: #451A4D; margin: 0 0 0.5rem 0; letter-spacing: -0.02em;">{title_html}</h1>{subtitle_html}</div>'
    st.markdown(html, unsafe_allow_html=True)


def card(title: str, content: str, accent: bool = False, icon: str = ""):
    """
    Tarjeta con estilo profesional.
    
    Args:
        title: Título de la tarjeta
        content: Contenido HTML o texto
        accent: Si True, usa colores dorados
        icon: Emoji o icon (opcional)
    """
    bg_color = "#FEF9E7" if accent else "white"
    border_color = "#DAA520" if accent else "#E0DCD5"
    title_color = "#A942EA" if not accent else "#B8860B"
    title_html = f'{icon} {title}' if icon else title
    html = f'<div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);"><h3 style="font-family: \'Montserrat\', sans-serif; font-size: 1.25rem; font-weight: 600; color: {title_color}; margin: 0 0 1rem 0;">{title_html}</h3><p style="color: #5F577A; line-height: 1.6; margin: 0; font-family: \'Montserrat\', sans-serif;">{content}</p></div>'
    st.markdown(html, unsafe_allow_html=True)


def alert(
    message: str,
    alert_type: Literal["success", "error", "warning", "info"] = "info",
    title: str = ""
):
    """
    Alerta con estilos profesionales.
    
    Args:
        message: Mensaje a mostrar
        alert_type: Tipo de alerta (success, error, warning, info)
        title: Título de la alerta (opcional)
    """
    colors = {
        "success": {"bg": "#ECFDF5", "border": "#10B981", "color": "#065F46", "icon": "✓"},
        "error": {"bg": "#FEE2E2", "border": "#EF4444", "color": "#7F1D1D", "icon": "✕"},
        "warning": {"bg": "#FFFBEB", "border": "#F59E0B", "color": "#78350F", "icon": "!"},
        "info": {"bg": "#EFF6FF", "border": "#3B82F6", "color": "#1E3A8A", "icon": "i"},
    }
    
    style = colors.get(alert_type, colors["info"])
    title_html = f'<p style="font-weight: 600; margin: 0 0 0.25rem 0;">{title}</p>' if title else ''
    
    html = f'<div style="background-color: {style["bg"]}; border-left: 4px solid {style["border"]}; padding: 1rem 1.25rem; border-radius: 6px; margin-bottom: 1rem;"><div style="display: flex; align-items: flex-start; gap: 0.75rem;"><span style="color: {style["border"]}; font-weight: 700; font-size: 1.25rem; line-height: 1;">{style["icon"]}</span><div style="color: {style["color"]};">{title_html}<p style="font-size: 0.95rem; line-height: 1.5; margin: 0;">{message}</p></div></div></div>'
    st.markdown(html, unsafe_allow_html=True)


def section_divider(title: str = ""):
    """
    Divisor de sección con opcionalmente un título.
    
    Args:
        title: Título de la sección (opcional)
    """
    if title:
        html = f'<h2 style="font-family: \'Playfair Display\', serif; font-size: 1.875rem; font-weight: 700; color: #6B2E6F; margin-top: 2rem; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 2px solid #E0DCD5;">{title}</h2>'
    else:
        html = '<hr style="border: none; border-top: 2px solid #E0DCD5; margin: 2rem 0;" />'
    st.markdown(html, unsafe_allow_html=True)


def stat_card(label: str, value: str, unit: str = "", icon: str = ""):
    """
    Tarjeta de estadística.
    
    Args:
        label: Etiqueta
        value: Valor numérico
        unit: Unidad (opcional)
        icon: Emoji o icon (opcional)
    """
    icon_html = f'<span style="font-size: 1.75rem; margin-right: 0.75rem;">{icon}</span>' if icon else ''
    unit_html = f'<p style="color: #75687F; font-size: 0.875rem; margin: 0.5rem 0 0 0;">{unit}</p>' if unit else ''
    html = f'<div style="background-color: white; border: 1px solid #E0DCD5; border-radius: 8px; padding: 1.5rem; text-align: center; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); margin-bottom: 1rem;"><div style="margin-bottom: 0.5rem;">{icon_html}</div><p style="color: #75687F; font-size: 0.875rem; font-weight: 500; margin: 0 0 0.5rem 0; text-transform: uppercase; letter-spacing: 0.05em;">{label}</p><p style="color: #451A4D; font-size: 2rem; font-weight: 700; margin: 0; font-variant-numeric: tabular-nums;">{value}</p>{unit_html}</div>'
    st.markdown(html, unsafe_allow_html=True)


def progress_bar(label: str, value: float, total: float = 100):
    """
    Barra de progreso personalizada.
    
    Args:
        label: Etiqueta
        value: Valor actual
        total: Valor total (default: 100)
    """
    percentage = (value / total) * 100
    html = f'<div style="margin-bottom: 1rem;"><p style="font-family: \'Montserrat\', sans-serif; font-size: 0.875rem; font-weight: 500; color: #1F2937; margin-bottom: 0.5rem;">{label} <span style="color: #6C7281;">{value} / {total}</span></p><div style="width: 100%; height: 8px; background-color: #EEEBE5; border-radius: 4px; overflow: hidden;"><div style="width: {percentage}%; height: 100%; background-color: #A942EA; transition: width 0.3s ease;"></div></div></div>'
    st.markdown(html, unsafe_allow_html=True)


def empty_state(
    icon: str = "🔍",
    title: str = "Sin resultados",
    message: str = "No hay datos para mostrar"
):
    """
    Estado vacío profesional.
    """
    html = f'<div style="text-align: center; padding: 3rem 2rem; color: #6C7281;"><div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div><h3 style="font-family: \'Playfair Display\', serif; font-size: 1.25rem; color: #1F2937; margin-bottom: 0.5rem;">{title}</h3><p style="margin: 0;">{message}</p></div>'
    st.markdown(html, unsafe_allow_html=True)
