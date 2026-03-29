"""
Color palette for CogniData application
Based on professional psychology clinic color scheme
"""

# Main color palette - Professional Healthcare Theme
COLORS = {
    # Primary: Therapeutic Green - Represents trust, healing, wellbeing
    "primary": "#2E7D32",           # Main therapeutic green
    "primary_dark": "#1B5E20",      # Darker green for text emphasis
    "primary_light": "#81C784",     # Lighter green for hover states
    
    # Secondary: Professional Blue - Represents trust, professionalism, stability
    "secondary": "#1976D2",         # Professional blue
    "secondary_dark": "#1565C0",    # Darker blue
    "secondary_light": "#42A5F5",   # Lighter blue for hover states
    
    # Accent: Orange - Represents energy, hope, positivity
    "accent": "#F57C00",            # Warm orange/amber
    "accent_light": "#FFB74D",      # Light orange for highlights
    
    # Neutrals - Background and text
    "background": "#F5F5F5",        # Very light gray for sidebar
    "background_dark": "#FFFFFF",   # Pure white for content
    "border": "#E0E0E0",            # Light gray for borders
    
    # Text colors
    "text_dark": "#333333",         # Dark gray for primary text
    "text_light": "#666666",        # Medium gray for secondary text
    "text_muted": "#999999",        # Light gray for tertiary text
    
    # Status colors
    "success": "#2E7D32",           # Green (same as primary)
    "warning": "#F57C00",           # Orange (same as accent)
    "danger": "#D32F2F",            # Red for errors/alerts
    "info": "#1976D2",              # Blue (same as secondary)
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
    "therapeutic": {
        "primary": COLORS["primary"],
        "secondary": COLORS["secondary"],
        "accent": COLORS["accent"],
        "description": "Green + Blue + Orange - Calming and professional"
    },
    "clinical": {
        "primary": COLORS["secondary"],
        "secondary": COLORS["primary"],
        "accent": COLORS["accent"],
        "description": "Blue + Green + Orange - Professional and trustworthy"
    },
    "warm": {
        "primary": COLORS["accent"],
        "secondary": COLORS["primary"],
        "accent": COLORS["secondary"],
        "description": "Orange + Green + Blue - Warm and welcoming"
    },
}
