# Professional Theme - Integration Guide for CogniData

## One-Line Integration

Add this to the **very top** of your `app.py`, immediately after imports:

```python
import streamlit as st
from styles.professional_theme import inject_professional_css

# CRITICAL: Call this FIRST, before any st.title(), st.write(), etc.
inject_professional_css()

# Then your app code continues...
```

## Step-by-Step Integration

### Step 1: Import the Theme Module

```python
from styles.professional_theme import (
    inject_professional_css,      # Apply CSS to entire app
    create_custom_alert,           # Create styled alert banners
    get_color,                     # Get color values by name
)
```

### Step 2: Inject CSS at Startup

```python
def main():
    # MUST be the first Streamlit operation
    inject_professional_css()
    
    # Then your app continues normally
    st.title("My App")
    st.write("Content here...")

if __name__ == "__main__":
    main()
```

### Step 3: Replace Alert Messages

Replace Streamlit's default alerts with professional styled ones:

```python
# OLD (Streamlit default)
if no_patients:
    st.warning("No hay pacientes registrados...")

# NEW (Professional theme)
if no_patients:
    create_custom_alert(
        title="Sem Pacientes Registados",
        message="Nenhum paciente foi registado ainda.",
        alert_type="info"
    )
```

### Step 4: Use Custom Colors in HTML

```python
from styles.professional_theme import get_color

# Use colors in markdown/HTML
st.markdown(
    f'<p style="color: {get_color("purple_dark")}; font-weight: bold;">Title</p>',
    unsafe_allow_html=True
)
```

## Alert Types Reference

| Type | Color | Icon | Use Case |
|------|-------|------|----------|
| `"info"` | Soft pink + purple | ℹ️ | General information |
| `"success"` | Light green | ✅ | Successful actions |
| `"warning"` | Light yellow | ⚠️ | Cautions/warnings |
| `"error"` | Light red | ❌ | Error messages |

## Quick Examples

### Alert Banner
```python
create_custom_alert(
    title="Informação",
    message="Esta é uma mensagem informativa.",
    alert_type="info"
)
```

### Success Message
```python
create_custom_alert(
    title="Sucesso!",
    message="Operação realizada com êxito.",
    alert_type="success"
)
```

### Warning
```python
create_custom_alert(
    title="Atenção",
    message="Verifique os dados antes de continuar.",
    alert_type="warning"
)
```

### Error
```python
create_custom_alert(
    title="Erro",
    message="Não foi possível realizar a operação.",
    alert_type="error"
)
```

## Color Palette Quick Reference

```python
from styles.professional_theme import get_color

purple_vibrant = get_color("purple_vibrant")      # rgb(147, 32, 214)
purple_dark = get_color("purple_dark")            # rgb(61, 12, 77)
bg_main = get_color("bg_main")                    # rgb(249, 247, 249)
bg_alert = get_color("bg_alert")                  # rgb(243, 222, 241)
border_subtle = get_color("border_subtle")        # rgb(225, 225, 225)
text_dark = get_color("text_dark")                # rgb(50, 50, 50)
whatsapp_green = get_color("whatsapp_green")      # rgb(37, 211, 102)
white = get_color("white")                        # rgb(255, 255, 255)
```

## Common Patterns

### Styled Card/Container
```python
st.markdown(
    f"""
    <div class="card">
        <h3 style="color: {get_color('purple_dark')};">Title</h3>
        <p>Content here</p>
    </div>
    """,
    unsafe_allow_html=True
)
```

### Sidebar Header
```python
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1rem;">
            <p style="font-size: 1.5rem; font-weight: bold; color: {get_color('purple_dark')};">
                CogniData
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
```

### Styled Buttons
```python
# Streamlit buttons automatically get theme styling
if st.button("Submit", use_container_width=True):
    st.success("Success!")
```

## CSS Classes Available

```css
/* Card styling */
<div class="card">Content</div>

/* Container */
<div class="container">Content</div>

/* Text colors */
<span class="text-primary">Purple</span>
<span class="text-dark">Dark Purple</span>
<span class="text-success">Green</span>
<span class="text-muted">Gray</span>

/* Text sizes */
<p class="text-sm">Small</p>
<p class="text-md">Medium</p>
<p class="text-lg">Large</p>
<p class="text-xl">Extra Large</p>

/* Font weights */
<p class="font-normal">Normal</p>
<p class="font-semibold">Semibold</p>
<p class="font-bold">Bold</p>

/* Spacing */
<div class="p-md">Padding</div>
<div class="m-lg">Margin</div>

/* Text alignment */
<p class="text-center">Centered</p>
<p class="text-right">Right-aligned</p>
```

## Checklist for Integration

- [ ] Add import: `from styles.professional_theme import inject_professional_css`
- [ ] Call `inject_professional_css()` as first Streamlit operation in main()
- [ ] Replace `st.warning()` with `create_custom_alert(..., alert_type="info")`
- [ ] Replace `st.success()` with `create_custom_alert(..., alert_type="success")`
- [ ] Replace `st.error()` with `create_custom_alert(..., alert_type="error")`
- [ ] Test on mobile to verify responsive design
- [ ] Check colors match design specification
- [ ] Verify no user input is interpolated into CSS/HTML

## Troubleshooting

### CSS Not Applying?
1. Verify `inject_professional_css()` is called FIRST
2. Must be before any `st.title()`, `st.write()`, etc.
3. Check browser console for errors
4. Clear browser cache (Ctrl+Shift+Delete)

### Colors Look Different?
- RGB values are correct as specified
- Some browsers render colors slightly differently
- Clear cache and refresh page

### Performance Issues?
- CSS injection happens once at startup
- No runtime performance impact
- If you notice slowness, profile the app

## File Structure

```
cognidata/
├── app.py (MODIFIED: add inject_professional_css())
├── styles/
│   ├── __init__.py
│   ├── professional_theme.py (NEW)
│   ├── example_implementation.py (REFERENCE)
│   └── design-system.css (EXISTING)
├── THEME_CUSTOMIZATION_GUIDE.md (NEW)
└── THEME_INTEGRATION_QUICKSTART.md (THIS FILE)
```

## Next Steps

1. Copy `professional_theme.py` to `styles/` directory
2. Add import to `app.py`
3. Call `inject_professional_css()` at startup
4. Replace alert messages with `create_custom_alert()`
5. Test the app to verify styling
6. Customize colors in `COLORS` dict if needed

## Questions?

- Review the example in `styles/example_implementation.py`
- Check `THEME_CUSTOMIZATION_GUIDE.md` for detailed documentation
- All CSS classes are documented in `professional_theme.py`
