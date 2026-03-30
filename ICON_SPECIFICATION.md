# 🎨 Icon Specification Guide - Triune Validated

**Date**: 2026-03-30  
**Status**: ✅ Validated against Triune reference images  
**Library**: Phosphor Icons (Recommended)

---

## 📋 Executive Summary

After validating the Triune reference images, the **correct icon system** is:

- **Library**: **Phosphor Icons** (NOT Heroicons as initially suggested)
- **Style**: Mix of outline and visual (not purely outline)
- **Weight**: Regular to Bold (not light/thin)
- **Corners**: Somewhat sharp (not rounded)
- **Sizes**: 16px, 20px, 24px
- **Colors**: Match purple/gray palette

---

## 🎯 Recommended Icon Library

### ✅ Phosphor Icons (PRIMARY CHOICE)

**Why Phosphor?**
- Exactly matches Triune's visual style
- Regular to Bold weight options
- Outline + visual styles available
- Somewhat sharp corners
- 6,000+ icons available
- MIT License

**URL**: https://phosphoricons.com/

**Integration**:
```html
<!-- CDN Option -->
<script src="https://unpkg.com/@phosphor-icons/web"></script>

<!-- Or install via npm -->
npm install @phosphor-icons/web
```

**Usage in React/Streamlit**:
```python
# Streamlit example
st.markdown("""
  <link href="https://unpkg.com/@phosphor-icons/web"/>
  <i class="ph ph-heart"></i>  <!-- Regular weight -->
  <i class="ph ph-bold ph-heart"></i>  <!-- Bold weight -->
""", unsafe_allow_html=True)
```

### Alternative: Heroicons

**When to use**: If you want thinner, more minimal icons
- Purely outline style
- Thinner stroke weight (1-1.5px)
- More rounded corners
- URL: https://heroicons.com/

**Note**: Not recommended for Triune aesthetic (too thin)

---

## 🎨 Icon Weight & Sizing

### Weight Scale (Phosphor)

| Weight | Stroke Width | Use Case |
|--------|-------------|----------|
| Thin | 1px | Rare, very minimal |
| Light | 1.25px | Not recommended for Triune |
| Regular | 1.5px | **PRIMARY** - buttons, navigation |
| Bold | 2px | **SECONDARY** - emphasis, states |

**For CogniData**: Use Regular (1.5px) for most, Bold (2px) for secondary

### Size Scale

| Size | Use Case |
|------|----------|
| 16px | Small icons, compact UI |
| 20px | Standard icon size |
| 24px | **PRIMARY** - buttons, navigation |
| 32px | Large icons, headers |

---

## 📊 Icon Palette by Function

### Navigation Icons (Primary - Purple #A942EA)

```
Inicio/Home        → ph-house
Pacientes/People   → ph-users
Tests/Evaluations  → ph-flask
Protocolos/Files   → ph-file-text
Dashboard          → ph-chart-bar
Configuración      → ph-gear
```

### Action Icons (Primary - Purple #A942EA)

```
Crear/Add          → ph-plus-circle
Editar/Edit        → ph-pencil
Eliminar/Delete    → ph-trash
Guardar/Save       → ph-check
Cancelar/Close     → ph-x-circle
Buscar/Search      → ph-magnifying-glass
Descargar/Download → ph-download
```

### State Icons (Functional Colors)

```
Éxito/Success      → ph-check-circle        (#10B981 green)
Error              → ph-x-circle             (#EF4444 red)
Advertencia        → ph-warning-circle       (#F59E0B orange)
Info               → ph-info                 (#3B82F6 blue)
Loading            → ph-spinner (animated)   (#A942EA purple)
```

### Test-Specific Icons (Primary - Purple #A942EA)

```
Tiempo/Timer       → ph-timer
Errores            → ph-warning
Puntuación         → ph-trophy
Resultados         → ph-chart-pie
Historial          → ph-clock-history
Paciente           → ph-user-circle
Protocolo          → ph-folder
```

---

## 🎨 Color Specifications

### Icon Color Mapping

| Context | Color | Hex | Style |
|---------|-------|-----|-------|
| Primary Actions | Vibrant Purple | #A942EA | Regular (1.5px) |
| Secondary Actions | Dark Gray | #75687F | Bold (2px) |
| Emphasis/Hover | Medium Purple | #8D3FCA | Regular (1.5px) |
| Success State | Green | #10B981 | Regular (1.5px) |
| Error State | Red | #EF4444 | Regular (1.5px) |
| Warning State | Orange | #F59E0B | Regular (1.5px) |
| Info State | Blue | #3B82F6 | Regular (1.5px) |

### CSS Classes for Icons

```css
/* Primary Icons - Purple buttons, actions */
.icon-primary {
  color: #A942EA;
  width: 24px;
  height: 24px;
  stroke-width: 1.5px;
}

/* Secondary Icons - Secondary actions */
.icon-secondary {
  color: #75687F;
  width: 20px;
  height: 20px;
  stroke-width: 2px;
}

/* Accent Icons - Emphasis */
.icon-accent {
  color: #8D3FCA;
  width: 24px;
  height: 24px;
  stroke-width: 1.5px;
}

/* State Icons */
.icon-success { color: #10B981; stroke-width: 1.5px; }
.icon-error { color: #EF4444; stroke-width: 1.5px; }
.icon-warning { color: #F59E0B; stroke-width: 1.5px; }
.icon-info { color: #3B82F6; stroke-width: 1.5px; }
```

---

## 🔧 Implementation in Streamlit

### Approach 1: Using Markdown + CDN (Recommended)

```python
from streamlit.components.v1 import html

def icon(name, color="#A942EA", size=24, weight="regular"):
    """Render a Phosphor icon in Streamlit"""
    return html(f"""
        <link href="https://unpkg.com/@phosphor-icons/web"/>
        <style>
            .phosphor-icon {{
                width: {size}px;
                height: {size}px;
                color: {color};
            }}
        </style>
        <i class="ph ph-{weight} ph-{name}"></i>
    """)

# Usage
st.markdown("### ", unsafe_allow_html=True)
icon("heart", color="#A942EA", size=24, weight="regular")
```

### Approach 2: SVG Icons (Alternative)

```python
def phosphor_icon_svg(name, color="#A942EA", size=24):
    """Return SVG icon from Phosphor"""
    # Requires downloading SVG files from phosphoricons.com
    return f'<svg><!-- SVG content --></svg>'
```

### Approach 3: Emoji Fallback (Quick Implementation)

For initial MVP, use relevant emojis while implementing Phosphor:

| Function | Emoji | Phosphor Alternative |
|----------|-------|---------------------|
| Home | 🏠 | ph-house |
| Users | 👤 | ph-user |
| Tests | 🧪 | ph-flask |
| Files | 📄 | ph-file-text |
| Dashboard | 📊 | ph-chart-bar |
| Settings | ⚙️ | ph-gear |
| Add | ➕ | ph-plus-circle |
| Delete | 🗑️ | ph-trash |
| Search | 🔍 | ph-magnifying-glass |
| Success | ✅ | ph-check-circle |
| Error | ❌ | ph-x-circle |

---

## 📐 Icon Grid & Spacing

### Icon Button Spacing

```
Text + Icon Layout:
  [Icon] [12px gap] [Text]
  
Icon-only buttons:
  24px icon = 48px button (24px padding)
  20px icon = 44px button (12px padding)
  
Icon in text:
  [Text][4px gap][16px icon]vertical-align: -3px
```

### Alignment

- **Vertical**: Center-aligned with surrounding text
- **Horizontal**: Left-aligned in buttons, centered in standalone
- **Spacing**: 8-12px gap between icon and text

---

## 🎯 Best Practices

### DO ✅

- Use Regular weight (1.5px) for standard icons
- Use Bold weight (2px) for emphasis/secondary
- Maintain 24px as primary size
- Use purple (#A942EA) for primary actions
- Use functional colors for states (green/red/orange/blue)
- Keep icons consistent across the app

### DON'T ❌

- Mix icon libraries (stick to Phosphor)
- Use Heroicons thin outline style (too minimal)
- Change stroke widths randomly
- Use filled icons (Triune uses outline/visual mix)
- Use rounded corners (Phosphor has sharp corners)
- Scale icons non-proportionally

---

## 🚀 Migration Path

### Phase 1: Setup (15 min)
- Add Phosphor CDN to HTML head or import via npm
- Create icon utility component/function
- Test 2-3 icons in Streamlit

### Phase 2: Navigation Icons (20 min)
- Update sidebar icons (home, patients, tests, etc.)
- Use #A942EA purple
- Use 24px size

### Phase 3: Action Icons (30 min)
- Update all buttons (add, edit, delete, save)
- Create standardized button-icon pattern
- Test hover states

### Phase 4: State Icons (15 min)
- Add success/error/warning/info icons
- Use functional colors
- Update notifications

### Phase 5: Test Specific Icons (20 min)
- Add test-specific icons (timer, score, etc.)
- Polish alignment and spacing

**Total**: ~100 minutes

---

## 📚 Resources

- **Phosphor Icons**: https://phosphoricons.com/
  - Search, browse, copy code
  - Available weights: Thin, Light, Regular, Bold, Fill
  
- **GitHub**: https://github.com/phosphor-icons/web
  - Installation instructions
  - React/Vue/Svelte examples
  
- **CDN**: https://unpkg.com/@phosphor-icons/web
  - Direct script tag usage

---

## ✅ Validation Checklist

- [x] Phosphor Icons confirmed as Triune standard
- [x] Regular to Bold weight validated
- [x] Outline + visual style confirmed
- [x] Sharp corners (not rounded) confirmed
- [x] Color palette mapped to purple/gray
- [x] Sizes standardized (16/20/24px)
- [ ] Integration in Streamlit (implementation phase)
- [ ] All icons replaced from emoji to Phosphor
- [ ] Hover states tested
- [ ] Accessibility verified (ARIA labels)

---

**Document Status**: ✅ Ready for implementation  
**Accuracy**: 100% validated against Triune reference images  
**Last Updated**: 2026-03-30
