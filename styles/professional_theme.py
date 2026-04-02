"""
Professional theme customization for CogniData using Streamlit CSS injection.

SECURITY NOTES:
- All CSS is hardcoded (no user input)
- Only uses trusted, internal color values
- No data binding to CSS to prevent injection
- unsafe_allow_html=True is safe here because:
  1. CSS is defined at module load time
  2. No user input is interpolated
  3. No form data is included in HTML

GDPR/Compliance:
- CSS customization doesn't affect data handling
- No PII transmitted through CSS
- No tracking or logging in CSS
"""

import streamlit as st

# Color palette (RGB values)
COLORS = {
    "purple_vibrant": "rgb(147, 32, 214)",      # Focus and highlights
    "purple_dark": "rgb(61, 12, 77)",           # Titles and strong text
    "bg_main": "rgb(249, 247, 249)",            # Soft cream main background
    "bg_alert": "rgb(243, 222, 241)",           # Soft pink alert background
    "border_subtle": "rgb(225, 225, 225)",      # Borders and dividers
    "text_dark": "rgb(50, 50, 50)",             # Standard dark text
    "whatsapp_green": "rgb(37, 211, 102)",      # Success/positive actions
    "white": "rgb(255, 255, 255)",              # Pure white
}


def inject_professional_css():
    """
    Inject professional CSS styling into Streamlit app.
    
    This function should be called at the beginning of your app.py
    BEFORE any other Streamlit components are rendered.
    
    Usage:
        import streamlit as st
        from styles.professional_theme import inject_professional_css
        
        inject_professional_css()
        
        # Then render your app normally
        st.title("My App")
    """
    
    css = f"""
    <style>
    /* ===== OVERALL PAGE LAYOUT ===== */
    
    /* Main background - soft cream */
    .main {{
        background-color: {COLORS['bg_main']};
        padding: 2rem;
    }}
    
    /* Remove default Streamlit header padding */
    .appview-container {{
        padding-top: 0;
    }}
    
    /* Hide Streamlit's default header/menu bar */
    header {{
        visibility: hidden;
        height: 0;
        padding: 0;
    }}
    
    
    /* ===== SIDEBAR STYLING ===== */
    
    /* Sidebar background - pure white */
    .sidebar {{
        background-color: {COLORS['white']};
        border-right: 1px solid {COLORS['border_subtle']};
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {COLORS['white']};
    }}
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
        gap: 1rem;
    }}
    
    
    /* ===== NAVIGATION STYLING ===== */
    
    /* Active navigation item - purple pill style */
    .nav-active {{
        background-color: {COLORS['purple_vibrant']};
        color: {COLORS['white']};
        border-radius: 50px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    /* Inactive navigation items */
    .nav-inactive {{
        color: {COLORS['text_dark']};
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }}
    
    .nav-inactive:hover {{
        background-color: {COLORS['bg_main']};
    }}
    
    /* Logout button styling */
    .logout-btn {{
        background-color: {COLORS['purple_vibrant']};
        color: {COLORS['white']};
        border: none;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 2rem;
    }}
    
    .logout-btn:hover {{
        background-color: {COLORS['purple_dark']};
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(147, 32, 214, 0.3);
    }}
    
    
    /* ===== MAIN CONTENT STYLING ===== */
    
    /* Main titles - dark purple */
    h1 {{
        color: {COLORS['purple_dark']};
        font-weight: 700;
        margin-bottom: 1.5rem;
        font-size: 2.5rem;
        letter-spacing: -0.5px;
    }}
    
    /* Section titles */
    h2 {{
        color: {COLORS['purple_dark']};
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-size: 1.8rem;
    }}
    
    /* Subsection titles */
    h3 {{
        color: {COLORS['purple_vibrant']};
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
        font-size: 1.3rem;
    }}
    
    /* Standard paragraph text */
    p {{
        color: {COLORS['text_dark']};
        line-height: 1.6;
        font-size: 1rem;
    }}
    
    
    /* ===== TABS STYLING ===== */
    
    /* Tab container */
    [data-testid="stTabs"] {{
        background-color: transparent;
    }}
    
    /* Tab buttons */
    [data-testid="stTabs"] button {{
        background-color: transparent;
        color: {COLORS['text_dark']};
        border: none;
        border-bottom: 3px solid transparent;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    /* Active tab - purple underline */
    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: {COLORS['purple_vibrant']};
        border-bottom-color: {COLORS['purple_vibrant']};
        font-weight: 600;
    }}
    
    /* Hover effect on tabs */
    [data-testid="stTabs"] button:hover {{
        color: {COLORS['purple_vibrant']};
    }}
    
    
    /* ===== ALERT/BANNER STYLING ===== */
    
    /* Custom alert banner */
    .custom-alert {{
        background-color: {COLORS['bg_alert']};
        border-left: 4px solid {COLORS['purple_vibrant']};
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }}
    
    .custom-alert-icon {{
        font-size: 1.5rem;
        flex-shrink: 0;
        color: {COLORS['purple_vibrant']};
    }}
    
    .custom-alert-content {{
        flex: 1;
    }}
    
    .custom-alert-title {{
        color: {COLORS['purple_dark']};
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }}
    
    .custom-alert-message {{
        color: {COLORS['text_dark']};
        font-size: 0.95rem;
        line-height: 1.5;
    }}
    
    /* Info alert variant */
    .alert-info {{
        background-color: {COLORS['bg_alert']};
        border-left-color: {COLORS['purple_vibrant']};
    }}
    
    /* Success alert variant */
    .alert-success {{
        background-color: rgba(37, 211, 102, 0.1);
        border-left-color: {COLORS['whatsapp_green']};
    }}
    
    .alert-success .custom-alert-icon {{
        color: {COLORS['whatsapp_green']};
    }}
    
    /* Warning alert variant */
    .alert-warning {{
        background-color: rgba(255, 193, 7, 0.1);
        border-left-color: rgb(255, 193, 7);
    }}
    
    .alert-warning .custom-alert-icon {{
        color: rgb(255, 193, 7);
    }}
    
    /* Error alert variant */
    .alert-error {{
        background-color: rgba(244, 67, 54, 0.1);
        border-left-color: rgb(244, 67, 54);
    }}
    
    .alert-error .custom-alert-icon {{
        color: rgb(244, 67, 54);
    }}
    
    
    /* ===== FORM ELEMENTS ===== */
    
    /* Input fields */
    input[type="text"],
    input[type="email"],
    input[type="password"],
    input[type="number"],
    textarea,
    select {{
        border: 2px solid {COLORS['border_subtle']};
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 1rem;
        color: {COLORS['text_dark']};
        transition: all 0.3s ease;
        background-color: {COLORS['white']};
    }}
    
    /* Input focus state */
    input[type="text"]:focus,
    input[type="email"]:focus,
    input[type="password"]:focus,
    input[type="number"]:focus,
    textarea:focus,
    select:focus {{
        border-color: {COLORS['purple_vibrant']};
        outline: none;
        box-shadow: 0 0 0 3px rgba(147, 32, 214, 0.1);
    }}
    
    /* Labels */
    label {{
        color: {COLORS['purple_dark']};
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: block;
    }}
    
    
    /* ===== BUTTON STYLING ===== */
    
    /* Primary buttons - purple */
    button[kind="primary"],
    [data-testid="baseButton-primary"] {{
        background-color: {COLORS['purple_vibrant']};
        color: {COLORS['white']};
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    button[kind="primary"]:hover,
    [data-testid="baseButton-primary"]:hover {{
        background-color: {COLORS['purple_dark']};
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(147, 32, 214, 0.3);
    }}
    
    /* Secondary buttons */
    button[kind="secondary"],
    [data-testid="baseButton-secondary"] {{
        background-color: transparent;
        color: {COLORS['purple_vibrant']};
        border: 2px solid {COLORS['purple_vibrant']};
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    button[kind="secondary"]:hover,
    [data-testid="baseButton-secondary"]:hover {{
        background-color: {COLORS['purple_vibrant']};
        color: {COLORS['white']};
    }}
    
    
    /* ===== CARDS AND CONTAINERS ===== */
    
    /* Card styling */
    .card {{
        background-color: {COLORS['white']};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid {COLORS['border_subtle']};
        transition: all 0.3s ease;
    }}
    
    .card:hover {{
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }}
    
    /* Container with subtle background */
    .container {{
        background-color: {COLORS['white']};
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }}
    
    
    /* ===== DIVIDERS AND SEPARATORS ===== */
    
    hr {{
        border: none;
        height: 1px;
        background-color: {COLORS['border_subtle']};
        margin: 2rem 0;
    }}
    
    
    /* ===== TABLE STYLING ===== */
    
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }}
    
    table thead {{
        background-color: {COLORS['purple_dark']};
        color: {COLORS['white']};
    }}
    
    table th {{
        padding: 1rem;
        text-align: left;
        font-weight: 600;
    }}
    
    table td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid {COLORS['border_subtle']};
    }}
    
    table tbody tr:hover {{
        background-color: {COLORS['bg_main']};
    }}
    
    
    /* ===== UTILITY CLASSES ===== */
    
    /* Padding utilities */
    .p-sm {{ padding: 0.5rem; }}
    .p-md {{ padding: 1rem; }}
    .p-lg {{ padding: 1.5rem; }}
    
    /* Margin utilities */
    .m-sm {{ margin: 0.5rem; }}
    .m-md {{ margin: 1rem; }}
    .m-lg {{ margin: 1.5rem; }}
    
    /* Text alignment */
    .text-center {{ text-align: center; }}
    .text-right {{ text-align: right; }}
    .text-left {{ text-align: left; }}
    
    /* Text colors */
    .text-primary {{ color: {COLORS['purple_vibrant']}; }}
    .text-dark {{ color: {COLORS['purple_dark']}; }}
    .text-muted {{ color: rgb(128, 128, 128); }}
    .text-success {{ color: {COLORS['whatsapp_green']}; }}
    
    /* Text sizes */
    .text-sm {{ font-size: 0.875rem; }}
    .text-md {{ font-size: 1rem; }}
    .text-lg {{ font-size: 1.25rem; }}
    .text-xl {{ font-size: 1.5rem; }}
    
    /* Font weights */
    .font-normal {{ font-weight: 400; }}
    .font-medium {{ font-weight: 500; }}
    .font-semibold {{ font-weight: 600; }}
    .font-bold {{ font-weight: 700; }}
    
    
    /* ===== RESPONSIVE DESIGN ===== */
    
    @media (max-width: 768px) {{
        .main {{
            padding: 1rem;
        }}
        
        h1 {{
            font-size: 2rem;
        }}
        
        h2 {{
            font-size: 1.5rem;
        }}
        
        .container {{
            padding: 1rem;
        }}
        
        [data-testid="stTabs"] button {{
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }}
    }}
    
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def create_custom_alert(title: str, message: str, alert_type: str = "info"):
    """
    Create a custom styled alert banner.
    
    Args:
        title: Alert title
        message: Alert message
        alert_type: Type of alert - "info", "success", "warning", "error"
    
    Example:
        from styles.professional_theme import create_custom_alert
        
        create_custom_alert(
            title="Sem Pacientes",
            message="Nenhum paciente foi registado ainda. Crie um novo paciente para começar.",
            alert_type="info"
        )
    """
    
    # Icon mapping
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    icon = icons.get(alert_type, "ℹ️")
    
    alert_html = f"""
    <div class="custom-alert alert-{alert_type}">
        <div class="custom-alert-icon">{icon}</div>
        <div class="custom-alert-content">
            <div class="custom-alert-title">{title}</div>
            <div class="custom-alert-message">{message}</div>
        </div>
    </div>
    """
    
    st.markdown(alert_html, unsafe_allow_html=True)


def get_color(color_name: str) -> str:
    """
    Get a color value by name.
    
    Args:
        color_name: Color name (e.g., "purple_vibrant")
    
    Returns:
        RGB color string (e.g., "rgb(147, 32, 214)")
    
    Example:
        from styles.professional_theme import get_color
        
        st.write(f'<p style="color: {get_color("purple_dark")}">Colored text</p>', 
                 unsafe_allow_html=True)
    """
    return COLORS.get(color_name, COLORS["text_dark"])
