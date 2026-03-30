# CogniData Design System
## Rediseño según estética Triune Neuropsicología

**Versión**: 1.0  
**Última actualización**: 2026-03-30  
**Estado**: Directrices de Diseño Completadas

---

## 📋 Índice

1. [Paleta de Colores](#paleta-de-colores)
2. [Tipografía](#tipografía)
3. [Iconografía](#iconografía)
4. [Componentes UI](#componentes-ui)
5. [Espaciado y Layout](#espaciado-y-layout)
6. [Tokens de Diseño](#tokens-de-diseño)
7. [Guía de Implementación](#guía-de-implementación)

---

## 1. Paleta de Colores

### Colores Primarios (Extraído de Triune Neuropsicología)

```
PÚRPURA VIBRANTE (Identidad de marca, confianza & profesionalismo)
├─ Primary-900: #451A4D    [Elementos oscuros, dark states]
├─ Primary-700: #8D3FCA    [Hover states, énfasis secundario]
├─ Primary-600: #A942EA    [Botones primarios, acentos principales] ✨
└─ Primary-500: #B560F0    [Elementos interactivos, highlights]

GRISES NEUTROS (Extraído de Triune, fondos y texto)
├─ Gray-50:  #FFFFFF      [Fondo principal, card backgrounds]
├─ Gray-100: #F6F5F2      [Fondos secundarios, light areas] ← PRIMARIO
├─ Gray-200: #E0D8DE      [Bordes suaves, separadores]
├─ Gray-300: #D7D1DA      [Bordes estándar, disabled states]
├─ Gray-400: #B8BCC7      [Placeholder text, hints]
├─ Gray-600: #75687F      [Texto secundario]
├─ Gray-700: #6B7281      [Texto primario]
├─ Gray-900: #3F3A42      [Texto fuerte, títulos]
└─ Gray-950: #1F1D21      [Fondo oscuro, contrast máximo]

FUNCIONALES (Colores de estado mantenidos)
├─ Success-500: #10B981   [Estados positivos, confirmación]
├─ Success-100: #ECFDF5   [Fondo success]
├─ Warning-500: #F59E0B   [Advertencias, atención]
├─ Warning-100: #FFFBEB   [Fondo warning]
├─ Error-500:   #EF4444   [Errores, destructivas]
├─ Error-100:   #FEE2E2   [Fondo error]
└─ Info-500:    #3B82F6   [Información, help]
```

### Aplicación de Colores

| Elemento | Color | Justificación |
|----------|-------|---------------|
| Barra lateral | Primary-900 (#451A4D) | Autoridad, marca Triune |
| Encabezados/Títulos | Gray-900 | Legibilidad máxima |
| Botón primario | Primary-600 (#A942EA) | Acción principal, marca |
| Botón secundario | Gray-300 | Acción alternativa |
| Fondo de página | Gray-100 (#F6F5F2) | Limpieza visual (como Triune) |
| Tarjetas | White (#FFFFFF) | Claridad, separación |
| Texto primario | Gray-700 | Legibilidad óptima |
| Texto secundario | Gray-600 | Jerarquía visual |
| Bordes | Gray-200 | Sutil, no invasivo |
| Focus/Active | Primary-600 (#A942EA) | Visibilidad clara, marca |

---

## 2. Tipografía

### Familias Tipográficas

**Para Títulos & Encabezados:**
```
Font: "Playfair Display" (Serif elegante)
Fallback: "Georgia", serif
Peso: 700 (Bold) para títulos principales
       600 (SemiBold) para subtítulos
Espaciado de línea: 1.2
Uso: H1, H2, H3, labels de secciones principales
```

**Para Cuerpo & Formularios:**
```
Font: "Montserrat" (Sans-serif moderna)
Fallback: "Open Sans", "Segoe UI", sans-serif
Peso: 400 (Regular) para cuerpo
       500 (Medium) para labels
       600 (SemiBold) para énfasis
Espaciado de línea: 1.5
Uso: Párrafos, labels, inputs, datos numéricos
```

**Especificaciones por Elemento:**

```css
/* Títulos Principales */
h1 {
  font-family: "Playfair Display", Georgia, serif;
  font-size: 2.5rem;      /* 40px */
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #451A4D;
  margin-bottom: 1.5rem;
}

/* Subtítulos */
h2 {
  font-family: "Playfair Display", Georgia, serif;
  font-size: 1.875rem;    /* 30px */
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.01em;
  color: #8D3FCA;
  margin-bottom: 1rem;
}

/* Subtítulos Secundarios */
h3 {
  font-family: "Montserrat", "Open Sans", sans-serif;
  font-size: 1.25rem;     /* 20px */
  font-weight: 600;
  line-height: 1.3;
  color: #A942EA;
  margin-bottom: 0.75rem;
}

/* Cuerpo de Texto */
body, p {
  font-family: "Montserrat", "Open Sans", sans-serif;
  font-size: 1rem;        /* 16px */
  font-weight: 400;
  line-height: 1.5;
  color: #4B5563;
  letter-spacing: 0;
}

/* Labels de Formularios */
label {
  font-family: "Montserrat", "Open Sans", sans-serif;
  font-size: 0.875rem;    /* 14px */
  font-weight: 500;
  line-height: 1.4;
  color: #1F2937;
  margin-bottom: 0.375rem;
}

/* Texto Pequeño/Helper */
small, .text-sm {
  font-family: "Montserrat", "Open Sans", sans-serif;
  font-size: 0.813rem;    /* 13px */
  font-weight: 400;
  line-height: 1.4;
  color: #6C7281;
}

/* Números/Datos */
.data-value, .metric {
  font-family: "Montserrat", "Open Sans", sans-serif;
  font-size: 1.5rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0;
}
```

### Jerarquía Tipográfica

```
H1  → Títulos principales de página (40px)
H2  → Títulos de secciones (30px)
H3  → Subtítulos subsecciones (20px)
H4  → Labels importantes (16px, bold)
Body → Párrafos principales (16px)
Small → Texto auxiliar, hints (13px)
```

---

## 3. Iconografía

### Librería Recomendada (Validada contra Triune)

**✅ Phosphor Icons (Recomendado)**
- URL: https://phosphoricons.com/
- Estilo: **Mezcla de outline y visual** (como Triune)
- Peso: **Regular a Bold** (no solo Light)
- Esquinas: **Algo agudas** (no completamente redondeadas)
- Tamaño estándar: 24px, 20px, 16px
- Licencia: MIT (libre)
- **POR QUÉ**: Coincide exactamente con el estilo visual de Triune

**Alternativa: Heroicons**
- URL: https://heroicons.com/
- Estilo: Outline (líneas finas)
- Peso: 1-1.5px (más delgado que Phosphor)
- ⚠️ NOTA: Más fino que lo que usa Triune
- Licencia: MIT (libre)

### Iconos por Sección

```
NAVEGACIÓN PRINCIPAL
├─ Inicio → home (o dashboard)
├─ Pacientes → users (o people)
├─ Tests/Evaluaciones → beaker (o activity)
├─ Protocolos → document-text (o file-text)
├─ Dashboard → chart-bar (o bar-chart)
└─ Configuración → cog (o settings)

ACCIONES COMUNES
├─ Crear/Nuevo → plus
├─ Editar → pencil (o edit)
├─ Eliminar → trash (o x-circle)
├─ Guardar → check (o save)
├─ Cancelar → x (o close)
├─ Buscar → magnifying-glass (o search)
└─ Descargar/PDF → arrow-down-tray (o download)

ESTADOS & FEEDBACK
├─ Éxito → check-circle (verde)
├─ Error → exclamation-circle (rojo)
├─ Advertencia → exclamation-triangle (naranja)
├─ Info → information-circle (azul)
└─ Loading → spinner (animado)

COMUNES EN TESTS
├─ Tiempo/Cronómetro → clock
├─ Errores → x-mark
├─ Puntuación/Score → star
├─ Resultados → chart-pie
└─ Historial → history
```

### Especificaciones de Iconos (Validadas contra Triune)

```css
/* Iconos Primarios - Púrpura vibrante */
.icon-primary {
  width: 24px;
  height: 24px;
  stroke: #A942EA;           /* Primary-600 (púrpura vibrante) */
  stroke-width: 1.5px;       /* Regular a Bold */
  fill: none;                /* Outline style */
  color: #A942EA;
}

/* Iconos Secundarios - Gris oscuro */
.icon-secondary {
  width: 20px;
  height: 20px;
  stroke: #75687F;           /* Gray-600 (gris Triune) */
  stroke-width: 2px;         /* Bold */
  fill: none;                /* Outline style */
}

/* Iconos de Acentos - Púrpura medio */
.icon-accent {
  width: 24px;
  height: 24px;
  stroke: #8D3FCA;           /* Primary-700 (púrpura medio) */
  stroke-width: 1.5px;       /* Regular a Bold */
  fill: none;                /* Outline style */
}

/* Iconos en Botones */
.btn-icon {
  width: 20px;
  height: 20px;
  margin-right: 0.5rem;
  vertical-align: -3px;
  stroke-width: 1.5px;       /* Regular a Bold */
}

/* Iconos de Estado */
.icon-success {
  stroke: #10B981;
  stroke-width: 1.5px;
}

.icon-error {
  stroke: #EF4444;
  stroke-width: 1.5px;
}

.icon-warning {
  stroke: #F59E0B;
  stroke-width: 1.5px;
}

.icon-info {
  stroke: #3B82F6;
  stroke-width: 1.5px;
}

/* Spinner/Loading */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.icon-loading {
  animation: spin 1s linear infinite;
  stroke: #0066CC;
}
```

---

## 4. Componentes UI

### Inputs y Formularios

```css
/* Input Base */
input[type="text"],
input[type="email"],
input[type="password"],
input[type="number"],
textarea,
select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #E8E9EB;              /* Gray-200 */
  border-radius: 0.375rem;                 /* 6px */
  font-family: "Montserrat", "Open Sans", sans-serif;
  font-size: 1rem;
  color: #4B5563;                          /* Gray-700 */
  background-color: #FFFFFF;
  transition: border-color 0.2s, box-shadow 0.2s;
}

/* Input Focus */
input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: #0066CC;                   /* Primary-600 */
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

/* Input Disabled */
input:disabled,
textarea:disabled,
select:disabled {
  background-color: #F0F1F3;               /* Gray-100 */
  border-color: #D9DDE4;                   /* Gray-300 */
  color: #B8BCC7;                          /* Gray-400 */
  cursor: not-allowed;
}

/* Input Error */
input.error,
textarea.error,
select.error {
  border-color: #EF4444;                   /* Error-500 */
  background-color: #FEE2E2;               /* Error-100 */
  color: #991B1B;
}

input.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Select/Dropdown */
select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%236C7281' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 16px 12px;
  padding-right: 2.5rem;
}

/* Placeholder Text */
::placeholder {
  color: #B8BCC7;                          /* Gray-400 */
  font-style: italic;
}
```

### Botones

```css
/* Botón Base */
button, .btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;                 /* 6px */
  font-family: "Montserrat", "Open Sans", sans-serif;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

/* Botón Primario */
.btn-primary {
  background-color: #0066CC;               /* Primary-600 */
  color: white;
  border: 1px solid #0066CC;
}

.btn-primary:hover {
  background-color: #0052A3;               /* Primary-700 */
  border-color: #0052A3;
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.15);
}

.btn-primary:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.2);
}

.btn-primary:active {
  background-color: #003A5C;               /* Primary-800 */
  transform: translateY(1px);
}

.btn-primary:disabled {
  background-color: #D9DDE4;               /* Gray-300 */
  border-color: #D9DDE4;
  color: #B8BCC7;
  cursor: not-allowed;
}

/* Botón Secundario (con acento dorado) */
.btn-secondary {
  background-color: #FEF9E7;               /* Accent-100 */
  color: #B8860B;                          /* Accent-700 */
  border: 1px solid #DAA520;               /* Accent-600 */
}

.btn-secondary:hover {
  background-color: #F0D958;               /* Accent-500 */
  border-color: #B8860B;
}

.btn-secondary:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(218, 165, 32, 0.2);
}

/* Botón Outline */
.btn-outline {
  background-color: transparent;
  color: #0066CC;                          /* Primary-600 */
  border: 1px solid #0066CC;
}

.btn-outline:hover {
  background-color: rgba(0, 102, 204, 0.05);
}

/* Botón Ghost (sin borde ni fondo) */
.btn-ghost {
  background-color: transparent;
  color: #0066CC;                          /* Primary-600 */
  border: 1px solid transparent;
}

.btn-ghost:hover {
  background-color: rgba(0, 102, 204, 0.1);
}

/* Botón Destructivo */
.btn-danger {
  background-color: #EF4444;               /* Error-500 */
  color: white;
  border: 1px solid #EF4444;
}

.btn-danger:hover {
  background-color: #DC2626;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
}

/* Botón Tamaños */
.btn-lg {
  padding: 1rem 2rem;
  font-size: 1.125rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-xs {
  padding: 0.375rem 0.75rem;
  font-size: 0.813rem;
}

/* Botón Cargando */
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
```

### Tarjetas (Cards)

```css
/* Card Base */
.card {
  background-color: white;
  border: 1px solid #E8E9EB;               /* Gray-200 */
  border-radius: 0.5rem;                   /* 8px */
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.card:hover {
  border-color: #D9DDE4;                   /* Gray-300 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #E8E9EB;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #001F3F;                          /* Primary-900 */
  margin: 0;
}

/* Card Content */
.card-content {
  color: #4B5563;                          /* Gray-700 */
  line-height: 1.5;
}

/* Card Footer */
.card-footer {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #E8E9EB;
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

/* Card Variantes */
.card.card-elevated {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card.card-accent {
  border-left: 4px solid #DAA520;          /* Accent-600 */
}

.card.card-highlight {
  background-color: #FEF9E7;               /* Accent-100 */
  border-color: #F0D958;                   /* Accent-500 */
}

.card.card-success {
  border-left: 4px solid #10B981;
}

.card.card-error {
  border-left: 4px solid #EF4444;
}
```

### Tablas

```css
table {
  width: 100%;
  border-collapse: collapse;
  font-family: "Montserrat", "Open Sans", sans-serif;
}

thead {
  background-color: #F8F9FA;               /* Gray-50 */
  border-bottom: 2px solid #E8E9EB;       /* Gray-200 */
}

thead th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #001F3F;                          /* Primary-900 */
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

tbody tr {
  border-bottom: 1px solid #E8E9EB;       /* Gray-200 */
  transition: background-color 0.15s;
}

tbody tr:hover {
  background-color: #F8F9FA;               /* Gray-50 */
}

tbody tr:last-child {
  border-bottom: none;
}

tbody td {
  padding: 1rem;
  color: #4B5563;                          /* Gray-700 */
  font-size: 0.95rem;
}

/* Data cell emphasis */
tbody td.data {
  font-weight: 600;
  color: #001F3F;                          /* Primary-900 */
  font-variant-numeric: tabular-nums;
}

/* Row alternado (zebra striping) */
tbody tr:nth-child(even) {
  background-color: #FAFBFC;
}
```

### Modales/Dialogs

```css
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #E8E9EB;       /* Gray-200 */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: #001F3F;                          /* Primary-900 */
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6C7281;                          /* Gray-600 */
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: #001F3F;
}

.modal-body {
  padding: 1.5rem;
  color: #4B5563;                          /* Gray-700 */
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #E8E9EB;          /* Gray-200 */
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}
```

### Alertas

```css
.alert {
  padding: 1rem 1.25rem;
  border-radius: 0.375rem;
  border-left: 4px solid;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

/* Alert Success */
.alert-success {
  background-color: #ECFDF5;               /* Success-100 */
  border-color: #10B981;                   /* Success-500 */
  color: #065F46;
}

.alert-success .alert-icon {
  color: #10B981;
}

/* Alert Error */
.alert-error {
  background-color: #FEE2E2;               /* Error-100 */
  border-color: #EF4444;                   /* Error-500 */
  color: #7F1D1D;
}

.alert-error .alert-icon {
  color: #EF4444;
}

/* Alert Warning */
.alert-warning {
  background-color: #FFFBEB;               /* Warning-100 */
  border-color: #F59E0B;                   /* Warning-500 */
  color: #78350F;
}

.alert-warning .alert-icon {
  color: #F59E0B;
}

/* Alert Info */
.alert-info {
  background-color: #EFF6FF;
  border-color: #3B82F6;                   /* Info-500 */
  color: #1E3A8A;
}

.alert-info .alert-icon {
  color: #3B82F6;
}

.alert-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.alert-message {
  font-size: 0.95rem;
  line-height: 1.5;
}

.alert-close {
  background: none;
  border: none;
  color: currentColor;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
  font-size: 1.25rem;
}
```

---

## 5. Espaciado y Layout

### Sistema de Espaciado (Escala 4px)

```css
:root {
  --spacing-xs: 0.25rem;  /* 4px */
  --spacing-sm: 0.5rem;   /* 8px */
  --spacing-md: 1rem;     /* 16px */
  --spacing-lg: 1.5rem;   /* 24px */
  --spacing-xl: 2rem;     /* 32px */
  --spacing-2xl: 3rem;    /* 48px */
  --spacing-3xl: 4rem;    /* 64px */
}
```

### Aplicación de Espaciado

```css
/* Page/Container */
main {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-2xl);
}

/* Section Spacing */
section {
  margin-bottom: var(--spacing-3xl);
}

section:last-child {
  margin-bottom: 0;
}

/* Espaciado Interior */
.card {
  padding: var(--spacing-lg);
}

.card.card-compact {
  padding: var(--spacing-md);
}

/* Gap entre elementos */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

.flex-group {
  display: flex;
  gap: var(--spacing-md);
}

.flex-group.tight {
  gap: var(--spacing-sm);
}

.flex-group.wide {
  gap: var(--spacing-lg);
}
```

### Breakpoints

```css
/* Mobile First */
@media (min-width: 640px) {
  /* small devices */
}

@media (min-width: 768px) {
  /* tablets */
  main { padding: var(--spacing-xl); }
}

@media (min-width: 1024px) {
  /* small desktops */
  main { padding: var(--spacing-2xl); }
}

@media (min-width: 1280px) {
  /* large desktops */
}
```

---

## 6. Tokens de Diseño

Tabla de referencia rápida para todo el sistema:

```yaml
# COLORES
Primary:
  900: "#001F3F"
  800: "#003A5C"
  700: "#0052A3"
  600: "#0066CC"
  500: "#1A75B9"

Accent:
  700: "#B8860B"
  600: "#DAA520"
  500: "#F0D958"
  100: "#FEF9E7"

Gray:
  50: "#F8F9FA"
  100: "#F0F1F3"
  200: "#E8E9EB"
  300: "#D9DDE4"
  400: "#B8BCC7"
  600: "#6C7281"
  700: "#4B5563"
  900: "#1F2937"
  950: "#111827"

# TIPOGRAFÍA
Serif:
  Family: "Playfair Display"
  Fallback: Georgia, serif

Sans:
  Family: "Montserrat"
  Fallback: "Open Sans", sans-serif

# BORDER RADIUS
Sizes:
  xs: "0.25rem"   (4px)
  sm: "0.375rem"  (6px)
  md: "0.5rem"    (8px)
  lg: "0.75rem"   (12px)
  full: "9999px"  (circular)

# SOMBRAS
Shadow:
  sm: "0 1px 2px rgba(0, 0, 0, 0.05)"
  base: "0 1px 3px rgba(0, 0, 0, 0.1)"
  md: "0 4px 12px rgba(0, 0, 0, 0.08)"
  lg: "0 10px 40px rgba(0, 0, 0, 0.15)"

# TRANSICIONES
Duration:
  Fast: "0.15s"
  Base: "0.2s"
  Slow: "0.3s"

Timing:
  ease-in-out
  ease

# ESPACIADO
Scale:
  xs: "0.25rem"   (4px)
  sm: "0.5rem"    (8px)
  md: "1rem"      (16px)
  lg: "1.5rem"    (24px)
  xl: "2rem"      (32px)
  2xl: "3rem"     (48px)
  3xl: "4rem"     (64px)
```

---

## 7. Guía de Implementación

### Paso 1: Importar Fuentes

```html
<!-- En <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">
```

### Paso 2: Importar Iconos

**Opción A - Heroicons CDN:**
```html
<!-- En <head> -->
<script src="https://cdn.jsdelivr.net/npm/heroicons@2/dist/outline/index.min.js"></script>
```

**Opción B - Usando SVG directo:**
```html
<svg class="icon-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor">
  <!-- path aquí -->
</svg>
```

### Paso 3: Estructura HTML Base

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CogniData - Evaluación Neuropsicológica</title>
  <link rel="stylesheet" href="css/design-system.css">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body>
  <div class="app-container">
    <!-- Sidebar Navigation -->
    <aside class="sidebar">
      <!-- Navigation Items -->
    </aside>
    
    <!-- Main Content -->
    <main class="main-content">
      <!-- Page Content -->
    </main>
  </div>
</body>
</html>
```

### Paso 4: Personalizar en Streamlit

Para Streamlit, usar `st.markdown()` con CSS personalizado:

```python
import streamlit as st

# Configurar custom CSS
custom_css = """
<style>
:root {
    --primary-900: #001F3F;
    --primary-600: #0066CC;
    --accent-600: #DAA520;
    --gray-50: #F8F9FA;
    --gray-700: #4B5563;
}

@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Montserrat:wght@400;500;600&display=swap');

body {
    font-family: "Montserrat", sans-serif;
    background-color: var(--gray-50);
    color: var(--gray-700);
}

h1, h2, h3 {
    font-family: "Playfair Display", serif;
    color: var(--primary-900);
}

/* Streamlit customizations */
.stButton > button {
    background-color: var(--primary-600);
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #0052A3;
}

.stTextInput > div > div > input {
    border: 1px solid #E8E9EB !important;
    border-radius: 6px !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--primary-600) !important;
    box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)
```

### Paso 5: Componentes Reutilizables

Crear archivo `components/design_components.py`:

```python
import streamlit as st

def header(title: str, subtitle: str = ""):
    """Header con estilo profesional"""
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="
            font-family: 'Playfair Display', serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: #001F3F;
            margin: 0 0 0.5rem 0;
        ">{title}</h1>
        {f'<p style="font-size: 1.1rem; color: #6C7281; margin: 0;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def card(title: str, content: str, accent: bool = False):
    """Tarjeta con estilo profesional"""
    bg_color = "#FEF9E7" if accent else "white"
    border_color = "#DAA520" if accent else "#E8E9EB"
    
    st.markdown(f"""
    <div style="
        background-color: {bg_color};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    ">
        <h3 style="
            font-family: 'Montserrat', sans-serif;
            font-size: 1.25rem;
            font-weight: 600;
            color: #0066CC;
            margin: 0 0 1rem 0;
        ">{title}</h3>
        <p style="
            color: #4B5563;
            line-height: 1.5;
            margin: 0;
        ">{content}</p>
    </div>
    """, unsafe_allow_html=True)

def alert(message: str, alert_type: str = "info"):
    """Alerta con estilos profesionales"""
    alert_styles = {
        "success": {"bg": "#ECFDF5", "border": "#10B981", "color": "#065F46"},
        "error": {"bg": "#FEE2E2", "border": "#EF4444", "color": "#7F1D1D"},
        "warning": {"bg": "#FFFBEB", "border": "#F59E0B", "color": "#78350F"},
        "info": {"bg": "#EFF6FF", "border": "#3B82F6", "color": "#1E3A8A"},
    }
    
    style = alert_styles.get(alert_type, alert_styles["info"])
    
    st.markdown(f"""
    <div style="
        background-color: {style['bg']};
        border-left: 4px solid {style['border']};
        padding: 1rem 1.25rem;
        border-radius: 6px;
        color: {style['color']};
    ">
        {message}
    </div>
    """, unsafe_allow_html=True)
```

---

## Checklist de Implementación

- [ ] Descargar y importar fuentes (Playfair Display + Montserrat)
- [ ] Crear archivo CSS principal con tokens de diseño
- [ ] Implementar colores en tema Streamlit (si aplica)
- [ ] Reemplazar iconos actuales por Heroicons outline
- [ ] Rediseñar componentes (botones, inputs, tarjetas)
- [ ] Aplicar espaciado consistente
- [ ] Revisar contraste de colores (WCAG AA mínimo)
- [ ] Probar en diferentes dispositivos (mobile, tablet, desktop)
- [ ] Validar legibilidad con contenido real
- [ ] Documentar guía de estilo para futuros desarrolladores

---

## Recursos Externos

- **Playfair Display**: https://fonts.google.com/specimen/Playfair+Display
- **Montserrat**: https://fonts.google.com/specimen/Montserrat
- **Heroicons**: https://heroicons.com/
- **Phosphor Icons**: https://phosphoricons.com/
- **WCAG Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Color Palette Generator**: https://coolors.co/

---

## Notas Finales

Este sistema de diseño mantiene:
- ✅ Profesionalismo médico/neuropsicológico
- ✅ Limpieza visual y espaciado generoso
- ✅ Accesibilidad (WCAG AA)
- ✅ Consistencia en toda la aplicación
- ✅ Flexibilidad para futuras extensiones
- ✅ Legibilidad óptima para largas sesiones de trabajo

El azul marino transmite confianza y autoridad mientras que el dorado suave añade calidez humana, creando el balance perfecto para una herramienta neuropsicológica profesional.
