# Guía de Implementación del Design System Triune en CogniData

**Fecha**: 2026-03-30  
**Versión**: 1.0  
**Estado**: Listo para Implementación

---

## 📋 Resumen

Se ha creado un sistema de diseño completo siguiendo la estética profesional de Triune Neuropsicología. Este documento proporciona instrucciones paso a paso para integrar el nuevo sistema en CogniData.

## 📁 Archivos Creados

```
/cognidata/
├── DESIGN_SYSTEM.md                    # Documentación completa del sistema
├── styles/
│   └── design-system.css               # CSS puro (22KB)
└── components/
    ├── __init__.py
    └── design_components.py             # Componentes Streamlit personalizados
```

## 🚀 Cómo Implementar

### Fase 1: Configuración Inicial (15 minutos)

#### 1.1 Aplicar el Design System en app.py

Agrega al inicio de tu archivo `app.py`:

```python
# En la parte superior del archivo
import sys
sys.path.insert(0, str(Path(__file__).parent))

from components.design_components import apply_design_system

# En la función main()
def main():
    # Aplicar el design system primero
    apply_design_system()
    
    # Resto del código...
```

#### 1.2 Reemplazar st.title(), st.header() con componentes personalizados

**Antes:**
```python
st.title("Mi Título")
st.markdown("Subtítulo")
```

**Después:**
```python
from components.design_components import header

header(
    title="Mi Título",
    subtitle="Subtítulo descriptivo",
    icon="🧪"
)
```

### Fase 2: Actualización de Colores (20 minutos)

#### 2.1 Reemplazar el tema actual

En el archivo `.streamlit/config.toml`, reemplaza la sección de temas:

```toml
[theme]
primaryColor = "#A942EA"      # Púrpura Triune (vibrante)
backgroundColor = "#F6F5F2"   # Gris ultra claro (como Triune)
secondaryBackgroundColor = "#FFFFFF"
textColor = "#75687F"         # Gris oscuro (como Triune)
font = "sans serif"
```

#### 2.2 Actualizar los Iconos (Phosphor Icons - Validado contra Triune)

⭐ **IMPORTANTE**: Reemplazar emojis por **Phosphor Icons** (validado contra Triune)

| Sección | Emoji Actual | Phosphor Icon | Descripción |
|---------|---|---|---|
| Inicio | 🏠 | `ph-house` | Home profesional |
| Pacientes | 👥 | `ph-users` | Grupo de usuarios |
| Tests | 🧪 | `ph-flask` | Evaluación científica |
| Protocolos | 📋 | `ph-file-text` | Documento formal |
| Dashboard | 📈 | `ph-chart-bar` | Gráficos |
| Config | ⚙️ | `ph-gear` | Configuración |
| Crear | ➕ | `ph-plus-circle` | Agregar nuevo |
| Editar | ✏️ | `ph-pencil` | Editar |
| Eliminar | 🗑️ | `ph-trash` | Eliminar |
| Guardar | 💾 | `ph-check` | Confirmar |
| Cancelar | ❌ | `ph-x-circle` | Cancelar |
| Buscar | 🔍 | `ph-magnifying-glass` | Buscar |

**Ver ICON_SPECIFICATION.md para detalles completos:**
- Pesos: Regular (1.5px) o Bold (2px)
- Colores: Púrpura (#A942EA) o funcionales
- Tamaños: 16px, 20px, 24px
- Instalación: CDN o npm

### Fase 3: Reemplazo de Componentes (45 minutos)

#### 3.1 Tarjetas de Información

**Antes:**
```python
st.info("Información importante")
```

**Después:**
```python
from components.design_components import card

card(
    title="Información Importante",
    content="Descripción detallada aquí",
    accent=False,
    icon="ℹ️"
)
```

#### 3.2 Alertas

**Antes:**
```python
st.success("¡Éxito!")
st.error("Error")
```

**Después:**
```python
from components.design_components import alert

alert(
    message="Operación completada correctamente",
    alert_type="success",
    title="¡Éxito!"
)

alert(
    message="Hubo un error al procesar",
    alert_type="error",
    title="Error"
)
```

#### 3.3 Encabezados de Sección

**Antes:**
```python
st.subheader("Mi Sección")
```

**Después:**
```python
from components.design_components import section_divider

section_divider("Mi Sección")
```

#### 3.4 Tarjetas de Estadísticas

**Antes:**
```python
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Pacientes", 45)
```

**Después:**
```python
from components.design_components import stat_card

col1, col2, col3 = st.columns(3)
with col1:
    stat_card(
        label="Pacientes Activos",
        value="45",
        unit="personas",
        icon="👤"
    )
```

### Fase 4: Actualización de Formularios (30 minutos)

Los inputs automáticamente adoptarán el nuevo estilo, pero verifica que:

#### 4.1 Inputs de texto

```python
# Automático - sin cambios necesarios
nombre = st.text_input("Nombre Completo")
```

#### 4.2 Selectores

```python
# Automático - sin cambios necesarios
tipo_test = st.selectbox(
    "Tipo de Test",
    ["TMT-A", "TAVEC", "Fluidez-FAS"]
)
```

#### 4.3 Botones

Los botones automáticamente usan el púrpura Triune. Para botones secundarios:

```python
# Primario (automático - púrpura vibrante)
if st.button("Guardar"):
    pass

# Para botones secundarios, usa markdown:
col1, col2 = st.columns(2)
with col1:
    if st.button("Guardar", use_container_width=True):
        pass
with col2:
    if st.button("Cancelar", use_container_width=True):
        pass
```

### Fase 5: Personalización de Páginas (Por página)

Para cada archivo en `app_pages/`, sigue este patrón:

```python
# En la parte superior
from components.design_components import (
    header, section_divider, card, alert, stat_card
)

def render():
    # Encabezado de página
    header(
        title="Título de la Página",
        subtitle="Descripción breve",
        icon="🎯"
    )
    
    # Secciones principales
    section_divider("Primera Sección")
    # ... contenido ...
    
    section_divider("Segunda Sección")
    # ... más contenido ...
```

## 🎨 Referencia Rápida de Colores

Para cuando necesites usar colores específicos en Markdown:

```python
# Púrpura vibrante (botones, acentos primarios)
st.markdown('<span style="color: #A942EA;">Texto púrpura</span>', unsafe_allow_html=True)

# Púrpura oscuro (textos oscuros, encabezados)
st.markdown('<span style="color: #451A4D;">Texto púrpura oscuro</span>', unsafe_allow_html=True)

# Gris profesional (texto secundario)
st.markdown('<span style="color: #75687F;">Texto gris</span>', unsafe_allow_html=True)

# Rojo (error)
st.markdown('<span style="color: #EF4444;">Texto rojo</span>', unsafe_allow_html=True)

# Verde (éxito)
st.markdown('<span style="color: #10B981;">Texto verde</span>', unsafe_allow_html=True)
```

## 📐 Espaciado Estándar

Usa estas medidas para mantener consistencia:

```
Grandes secciones:   3rem (48px)
Entre secciones:     2rem (32px)
Entre elementos:     1.5rem (24px)  ← Default
Entre filas:         1rem (16px)
Entre items cercanos: 0.5rem (8px)
Mínimo:              0.25rem (4px)
```

## 🔤 Guía de Tipografía

### Para Títulos (Serif - Playfair Display)

```python
st.markdown("""
<h1>Título Principal (40px, 700)</h1>
<h2>Subtítulo (30px, 700)</h2>
<h3>Encabezado Sección (20px, 600)</h3>
""", unsafe_allow_html=True)
```

### Para Cuerpo (Sans-Serif - Montserrat)

```python
st.markdown("""
<p>Párrafo normal (16px, 400)</p>
<p><strong>Texto destacado (16px, 600)</strong></p>
<small>Texto pequeño (13px, 400)</small>
""", unsafe_allow_html=True)
```

## 📱 Responsive Design

El sistema es automáticamente responsive para:
- Desktop (1280px+)
- Tablet (768px - 1279px)
- Mobile (320px - 767px)

No necesitas hacer cambios; Streamlit y CSS manejan la adaptación.

## ♿ Accesibilidad

El sistema cumple con WCAG AA:

✅ Contraste mínimo 4.5:1 para texto
✅ Fuentes legibles en pantalla
✅ Estados interactivos claros (focus visible)
✅ Colores no son la única forma de comunicación

## 🧪 Testing de la Implementación

Después de cada cambio, verifica:

```bash
# 1. Inicia la app
streamlit run app.py

# 2. Verifica visualmente:
# - Colors match the design system
# - Spacing is consistent
# - Fonts render correctly
# - Buttons and inputs look professional
# - Responsive works on mobile
```

## 📝 Checklist de Implementación

- [ ] Copiar DESIGN_SYSTEM.md y styles/design-system.css
- [ ] Crear components/design_components.py
- [ ] Actualizar app.py para aplicar design system
- [ ] Reemplazar st.title() con header()
- [ ] Actualizar .streamlit/config.toml con nuevos colores
- [ ] Cambiar emojis de navegación
- [ ] Reemplazar alertas (st.success → alert())
- [ ] Reemplazar tarjetas (st.metric → stat_card())
- [ ] Actualizar app_pages/inicio.py
- [ ] Actualizar app_pages/pacientes.py
- [ ] Actualizar app_pages/tests.py
- [ ] Actualizar app_pages/protocols.py
- [ ] Actualizar app_pages/dashboard.py
- [ ] Actualizar app_pages/configuracion.py
- [ ] Testear en desktop
- [ ] Testear en tablet
- [ ] Testear en mobile
- [ ] Revisar contraste de colores
- [ ] Commit: "style: apply Triune design system"

## 🎯 Estimación de Tiempo

| Fase | Tiempo | Complejidad |
|------|--------|-------------|
| Configuración inicial | 15 min | 🟢 Baja |
| Actualización colores | 20 min | 🟢 Baja |
| Reemplazo componentes | 45 min | 🟡 Media |
| Actualización formularios | 30 min | 🟡 Media |
| Personalización páginas | 2 horas | 🟡 Media |
| Testing completo | 30 min | 🟢 Baja |
| **Total** | **~4 horas** | **🟡 Media** |

## 🆘 Troubleshooting

### Los nuevos colores no aparecen

**Problema**: El CSS no se carga
**Solución**: 
```python
# Agrega al inicio de app.py
st.set_page_config(theme="light")  # Fuerza el tema claro
```

### Las fuentes no se cargan

**Problema**: Google Fonts bloqueado o sin conexión
**Solución**: Las fuentes se descargan como fallback (Georgia, Open Sans)

### Los inputs ven estilos antiguos

**Problema**: Cache de Streamlit
**Solución**: 
```bash
streamlit run app.py --logger.level=debug --client.caching=false
```

### Componentes se ven mal en mobile

**Problema**: Breakpoints no se aplican
**Solución**: Ya están incluidos en design-system.css; verifica viewport meta tag

## 📚 Recursos Adicionales

- **Design System completo**: DESIGN_SYSTEM.md (documento detallado)
- **CSS puro**: styles/design-system.css (para usos no-Streamlit)
- **Componentes**: components/design_components.py (reutilizables)
- **Colores de referencia**: CSS variables en :root

## 🤝 Contribuciones Futuras

Si necesitas extender el design system:

1. Agrega variables CSS nuevas en `design-system.css` (línea 30)
2. Crea nuevos componentes en `design_components.py`
3. Documenta en `DESIGN_SYSTEM.md`
4. Mantén la coherencia visual

## ✅ Conclusión

El design system está completamente documentado y listo para implementar. Todos los archivos necesarios están creados. Sigue el checklist anterior y tendrás CogniData con la estética profesional de Triune en aproximadamente 4 horas.

¡Buena suerte con la implementación! 🚀
