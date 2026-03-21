# Changelog - CogniData

## [0.2.0] - 2026-03-18

### ✨ Añadido

#### Tablas Normativas NEURONORMA Reales
- Implementadas tablas de conversión para 3 tests principales:
  - **TMT-A**: Trail Making Test - Parte A (tiempo → pe + percentil)
  - **TAVEC**: Test de Aprendizaje Verbal (total Lista A → pe + percentil)
  - **Fluidez-FAS**: Fluidez Verbal Fonológica (total palabras → pe + percentil)
- Estratificación por edad (50-64, 65+) y educación (0-7, 8-12, 13+ años)
- Interpolación lineal automática entre puntuaciones brutas
- Archivos JSON en `data/normative_tables/`

#### Calculador NEURONORMA Mejorado
- Carga automática de tablas JSON al iniciar
- Selección inteligente de rango edad/educación apropiado
- Búsqueda exacta + interpolación lineal
- Conversión percentil ↔ z-score bidireccional
- Clasificación clínica automática (Superior/Normal/Limítrofe/Deficitario)
- Fallback a simulación para tests sin tabla
- Información detallada de norma aplicada (fuente, rangos)

#### Generador de Informes PDF
- Informe profesional con ReportLab
- Estructura completa:
  - Encabezado con fecha de emisión
  - Datos demográficos del paciente (ID anónimo, edad, educación, lateralidad)
  - Tabla resumen de todos los tests (PB, PE, Percentil, Clasificación)
  - Color-coding por clasificación (verde/azul/amarillo/rojo)
  - Detalles por test con observaciones clínicas
  - Análisis del perfil cognitivo (media pe, puntos fuertes/débiles)
  - Pie de página con aviso RGPD
- Botón de descarga directa desde Dashboard
- Nombres automáticos: `informe_{paciente_id}_{timestamp}.pdf`
- Guardado en directorio `reports/`

#### Métodos del Modelo TestSession
- Añadidos `set_qualitative_data()` y `get_qualitative_data()`
- Serialización JSON consistente para todos los campos
- Compatibilidad completa con generador PDF

### 🐛 Corregido
- **Bug crítico**: AttributeError al generar PDF por falta de método `get_qualitative_data()` en TestSession
- Solución: Implementados métodos setter/getter para qualitative_data

### 📚 Documentación
- Creado `IMPLEMENTATION.md` con detalles técnicos completos
- Actualizado `README.md` con nuevas funcionalidades
- Actualizado `plan.md` con estado actual del proyecto
- Creado script de verificación `test_complete_flow.py`

### 🔬 Testing
- Verificado cálculo NEURONORMA con datos reales
- Probada generación PDF con 4 tests
- Validado flujo completo: Paciente → Test → Cálculo → PDF

### 📊 Métricas
- Líneas de código Python: ~6,500 líneas
- Archivos JSON de tablas: 3 (7.7KB total)
- Tests con normas reales: 3/6 (50%)
- PDFs generados exitosamente: ✅
- Tamaño promedio PDF: ~3.5KB

---

## [0.1.0] - 2026-03-17

### ✨ Lanzamiento Inicial

#### Core Features
- Aplicación Streamlit 100% Python
- Base de datos SQLite + SQLAlchemy ORM
- Gestión de pacientes anónimos (RGPD compliant)
- 6 tests neuropsicológicos completos:
  - TMT-A, TMT-B
  - TAVEC
  - Fluidez Verbal Fonológica (F-A-S)
  - Figura de Rey - Copia y Memoria

#### Funcionalidades
- Formularios específicos por test con validación
- Cronómetros integrados para tests temporales
- Contadores de errores (intrusiones, perseveraciones, etc.)
- Checklist clínico cualitativo
- Observaciones de proceso (texto libre)

#### Dashboard
- Gráfico de radar (perfil cognitivo)
- Gráfico de barras (percentiles)
- Tabla resumen de resultados
- Análisis automático (media pe, puntos fuertes/débiles)

#### Cálculo Normativo
- Motor de cálculo con SciPy
- Simulación basada en distribución normal (placeholder)
- Puntuación Escalar (pe, escala 1-19)
- Percentiles
- Clasificación clínica

#### Infraestructura
- Tema clínico (azul + slate)
- Interfaz ES-ES (español de España)
- Backup manual de base de datos
- Cascade delete para RGPD

### 📁 Estructura
- `app.py` (~700 líneas)
- Modelos: `Patient`, `TestSession`
- Servicios: `normatives.py`
- Configuración: `.streamlit/config.toml`
- Documentación: `README.md`, `USAGE.md`

---

## Roadmap

### [0.3.0] - Próxima versión
- [ ] Tablas NEURONORMA para TMT-B, Rey-Copia, Rey-Memoria
- [ ] Inclusión de gráficos Plotly en PDF
- [ ] Validación de tablas con literatura oficial
- [ ] Comparación longitudinal (evolución del paciente)

### [0.4.0] - Futuro
- [ ] Personalización PDF (logo, membrete, firma digital)
- [ ] Exportación de datos completos (JSON/CSV)
- [ ] Sincronización cloud opcional (Supabase)
- [ ] Modo PWA para tablets
- [ ] Tests E2E automatizados

---

**Mantenedores**: Equipo de Neuropsicología  
**Licencia**: Uso profesional clínico  
**NEURONORMA**: Peña-Casanova et al. (2009)
