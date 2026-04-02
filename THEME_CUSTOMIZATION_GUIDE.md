# Professional Theme Customization Guide

## Overview

This guide explains how to use the professional theme customization module to create a clean, modern Streamlit interface with a custom color palette.

## Features

✅ **Sidebar Styling**
- Pure white background
- Active navigation items styled as purple pills
- Rounded logout button

✅ **Main Content**
- Soft cream background
- Dark purple titles
- Professional typography

✅ **Tabs**
- Purple underline for active tabs
- Smooth transitions

✅ **Custom Alerts**
- Info, Success, Warning, Error variants
- Soft pink background with left border
- Icon support

✅ **Form Elements**
- Rounded input fields
- Purple focus state
- Clean label styling

✅ **Responsive Design**
- Mobile-friendly
- Adaptive spacing and sizing

## Quick Start

### 1. Import the Theme in app.py

```python
import streamlit as st
from styles.professional_theme import inject_professional_css, create_custom_alert, get_color

# IMPORTANT: Call this FIRST, before any st.title(), st.write(), etc.
inject_professional_css()

# Now render your app normally
st.title("CogniData - Neuropsychological Testing")
```

### 2. Use Custom Alerts

```python
from styles.professional_theme import create_custom_alert

# Info alert
create_custom_alert(
    title="Informação",
    message="Nenhum paciente foi registado ainda.",
    alert_type="info"
)

# Success alert
create_custom_alert(
    title="Sucesso!",
    message="Paciente registado com êxito.",
    alert_type="success"
)

# Warning alert
create_custom_alert(
    title="Atenção",
    message="Este paciente possui dados incompletos.",
    alert_type="warning"
)

# Error alert
create_custom_alert(
    title="Erro",
    message="Falha ao carregar os dados.",
    alert_type="error"
)
```

### 3. Use Color Variables

```python
from styles.professional_theme import get_color

# In markdown with HTML
st.markdown(
    f'<p style="color: {get_color("purple_dark")}; font-weight: bold;">Título Personalizado</p>',
    unsafe_allow_html=True
)

# Use in other contexts
purple_color = get_color("purple_vibrant")
green_color = get_color("whatsapp_green")
```

## Color Palette

### Available Colors

```python
COLORS = {
    "purple_vibrant": "rgb(147, 32, 214)",      # Main brand color
    "purple_dark": "rgb(61, 12, 77)",           # Titles and strong text
    "bg_main": "rgb(249, 247, 249)",            # Soft cream background
    "bg_alert": "rgb(243, 222, 241)",           # Soft pink alerts
    "border_subtle": "rgb(225, 225, 225)",      # Borders
    "text_dark": "rgb(50, 50, 50)",             # Standard text
    "whatsapp_green": "rgb(37, 211, 102)",      # Success/positive
    "white": "rgb(255, 255, 255)",              # Pure white
}
```

## CSS Classes

You can use these CSS classes in HTML/markdown:

### Text Colors
- `.text-primary` - Purple vibrant
- `.text-dark` - Dark purple
- `.text-muted` - Muted gray
- `.text-success` - WhatsApp green

### Text Sizes
- `.text-sm` - Small (0.875rem)
- `.text-md` - Medium (1rem)
- `.text-lg` - Large (1.25rem)
- `.text-xl` - Extra large (1.5rem)

### Font Weights
- `.font-normal` - Regular (400)
- `.font-medium` - Medium (500)
- `.font-semibold` - Semibold (600)
- `.font-bold` - Bold (700)

### Spacing
- `.p-sm` / `.m-sm` - Small padding/margin (0.5rem)
- `.p-md` / `.m-md` - Medium padding/margin (1rem)
- `.p-lg` / `.m-lg` - Large padding/margin (1.5rem)

### Card Styling
- `.card` - White card with shadow and hover effect
- `.container` - Large container with styling

### Text Alignment
- `.text-center` - Center aligned
- `.text-right` - Right aligned
- `.text-left` - Left aligned

## Example: Custom Alert Banner

```html
<div class="custom-alert alert-info">
    <div class="custom-alert-icon">ℹ️</div>
    <div class="custom-alert-content">
        <div class="custom-alert-title">Título</div>
        <div class="custom-alert-message">Mensagem detalhada</div>
    </div>
</div>
```

Or use the Python function:
```python
create_custom_alert("Título", "Mensagem", alert_type="info")
```

## Security Notes

✅ **Safe Practices**
- All CSS is hardcoded (no user input)
- Only uses trusted color values
- No data binding to CSS
- `unsafe_allow_html=True` is safe here because:
  1. CSS defined at module load time
  2. No user input interpolated
  3. No form data in HTML

❌ **DO NOT DO**
```python
# UNSAFE: Never interpolate user input into HTML/CSS
user_input = request.form.get('color')
st.markdown(f'<p style="color: {user_input}">Text</p>', unsafe_allow_html=True)
```

## Integration with Existing Pages

### Before (Plain Streamlit)
```python
import streamlit as st

st.title("Pacientes")
if not pacientes:
    st.warning("No hay pacientes registrados...")
```

### After (With Professional Theme)
```python
import streamlit as st
from styles.professional_theme import inject_professional_css, create_custom_alert

# Call once at app start
inject_professional_css()

st.title("Pacientes")
if not pacientes:
    create_custom_alert(
        title="Sem Pacientes",
        message="Nenhum paciente foi registado ainda. Crie um novo paciente para começar.",
        alert_type="info"
    )
```

## Sidebar Navigation Example

```python
import streamlit as st
from styles.professional_theme import inject_professional_css

# Inject CSS once at startup
inject_professional_css()

# Sidebar navigation
with st.sidebar:
    st.markdown('<div style="text-align: center; padding: 1rem; font-weight: bold; color: rgb(61, 12, 77);">CogniData</div>', unsafe_allow_html=True)
    
    selected = st.radio(
        "Navegação",
        ["Inicio", "Pacientes", "Tests", "Dashboard", "Configuração"]
    )
    
    # Logout button
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.user = None
        st.rerun()
```

## Customizing Colors

To change colors globally:

1. Edit `styles/professional_theme.py`
2. Modify the `COLORS` dictionary
3. Colors are injected into CSS automatically
4. Re-run your app

Example:
```python
COLORS = {
    "purple_vibrant": "rgb(180, 50, 240)",  # Changed
    "purple_dark": "rgb(80, 20, 100)",      # Changed
    # ... rest unchanged
}
```

## Responsive Mobile Design

The theme includes responsive breakpoints for mobile devices (768px and below):
- Reduced padding
- Smaller font sizes
- Adjusted spacing

No additional code needed - it's automatic!

## Troubleshooting

### Theme Not Applying?
- Ensure `inject_professional_css()` is called FIRST in your app
- It must be called before any Streamlit components
- Clear browser cache if styles seem outdated

### Colors Look Wrong?
- Check that RGB values are correct
- Verify no quotes or typos in color strings
- Clear browser cache

### Performance Issues?
- CSS is injected once at startup - performance impact is minimal
- No runtime overhead after initial injection

## Support

For questions or issues:
1. Check the code comments in `styles/professional_theme.py`
2. Review this guide's examples
3. Test colors in isolation with `st.markdown(..., unsafe_allow_html=True)`
