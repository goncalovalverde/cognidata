"""
Color palette for CogniData application
Based on modern neuropsychology clinic design (Triune Neuropsicología inspired)
"""

# Main color palette - Modern Neuropsychology Clinic Theme
COLORS = {
    # Primary: Modern Purple/Violet - Represents innovation, expertise, creativity
    "primary": "#7E57C2",           # Modern purple
    "primary_dark": "#5E35B1",      # Darker purple
    "primary_light": "#B39DDB",     # Lighter purple
    
    # Secondary: Professional Gray/Blue-Gray - Represents trust, stability
    "secondary": "#546E7A",         # Blue-gray (sophisticated)
    "secondary_dark": "#37474F",    # Darker gray
    "secondary_light": "#90A4AE",   # Lighter gray
    
    # Accent: Teal/Cyan - Represents healing, clarity, modern tech
    "accent": "#26C6DA",            # Modern teal
    "accent_light": "#80DEEA",      # Light teal for highlights
    
    # Neutrals - Background and text
    "background": "#F9F9F9",        # Almost white for sidebar
    "background_dark": "#FFFFFF",   # Pure white for content
    "border": "#E0E0E0",            # Light gray for borders
    
    # Text colors
    "text_dark": "#263238",         # Very dark blue-gray for primary text
    "text_light": "#607D8B",        # Medium gray for secondary text
    "text_muted": "#90A4AE",        # Light gray for tertiary text
    
    # Status colors
    "success": "#26A69A",           # Teal green
    "warning": "#FFA726",           # Warm orange
    "danger": "#EF5350",            # Red
    "info": "#29B6F6",              # Light blue
}

# Theme configuration
THEME = {
    "primary_color": COLORS["primary"],
    "secondary_color": COLORS["secondary"],
    "accent_color": COLORS["accent"],
    
    # Sidebar configuration
    "sidebar": {
        "background": COLORS["background"],
        "text": COLORS["text_dark"],
        "border": COLORS["primary"],
        "hover": f"{COLORS['primary_light']}22",  # With transparency
    },
    
    # Navigation menu
    "nav_menu": {
        "icon_color": COLORS["secondary"],
        "item_color": COLORS["text_dark"],
        "selected_color": COLORS["primary"],
        "hover_color": f"{COLORS['primary_light']}22",
        "selected_text_color": "#FFFFFF",
    },
    
    # Buttons
    "button": {
        "primary": COLORS["primary"],
        "secondary": COLORS["secondary"],
        "accent": COLORS["accent"],
        "text": "#FFFFFF",
    },
    
    # Forms
    "form": {
        "label_color": COLORS["text_dark"],
        "input_border": COLORS["border"],
        "input_focus": COLORS["primary"],
        "input_error": COLORS["danger"],
    },
    
    # Cards and containers
    "container": {
        "background": COLORS["background_dark"],
        "border": COLORS["border"],
        "shadow": "rgba(0, 0, 0, 0.1)",
    },
    
    # Typography
    "typography": {
        "heading": COLORS["primary"],
        "subheading": COLORS["secondary"],
        "body": COLORS["text_dark"],
        "caption": COLORS["text_light"],
    },
}


def get_color(color_name: str) -> str:
    """
    Get a color from the palette by name
    
    Example:
        color = get_color("primary")
        hover_color = get_color("primary_light")
    """
    return COLORS.get(color_name, COLORS["primary"])


def get_css_variables() -> str:
    """
    Generate CSS custom properties from color palette
    Useful for inline CSS styling
    """
    css = """
    <style>
    :root {
    """
    for name, value in COLORS.items():
        css_var_name = name.replace("_", "-")
        css += f"    --color-{css_var_name}: {value};\n"
    
    css += """    }
    </style>
    """
    return css


# Pre-defined color combinations for quick use
COLOR_SCHEMES = {
    "modern_purple": {
        "primary": COLORS["primary"],
        "secondary": COLORS["secondary"],
        "accent": COLORS["accent"],
        "description": "Purple + Gray + Teal - Modern and sophisticated"
    },
    "tech_forward": {
        "primary": COLORS["accent"],
        "secondary": COLORS["primary"],
        "accent": COLORS["secondary"],
        "description": "Teal + Purple + Gray - Tech-forward neuropsych"
    },
    "professional": {
        "primary": COLORS["secondary"],
        "secondary": COLORS["primary"],
        "accent": COLORS["accent"],
        "description": "Gray + Purple + Teal - Professional and elegant"
    },
}

