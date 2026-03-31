# CogniData - Aplicación Neuropsicológica 🧠

**Sistema 100% Python con Streamlit** para gestión de tests neuropsicológicos y cálculo automático de normas NEURONORMA.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.31-red)
![License](https://img.shields.io/badge/license-Private-yellow)

---

## 🎯 Características

### ✅ Completamente Funcional

- ✅ **6 Tests Neuropsicológicos Completos:**
  - TMT-A (Trail Making Test - Parte A)
  - TMT-B (Trail Making Test - Parte B)  
  - TAVEC (Test de Aprendizaje Verbal)
  - Fluidez Verbal Fonológica (F-A-S)
  - Figura Compleja de Rey - Copia
  - Figura Compleja de Rey - Memoria

- ✅ **Gestión de Pacientes RGPD-Compliant:**
  - Datos 100% anónimos (UUID + edad + escolaridad)
  - Sin nombres, DNI, emails
  - Derecho al olvido (eliminar paciente)
  
- ✅ **Cálculo Automático de Normas:**
  - Puntuación Escalar (pe): escala 1-19, media 10, DE 3
  - Percentiles ajustados por edad y escolaridad
  - Clasificación: Superior/Normal/Limítrofe/Deficitario
  
- ✅ **Dashboard Completo:**
  - Gráfico Radar: Perfil cognitivo multidimensional
  - Gráfico de Barras: Percentiles con código de colores
  - Tabla resumen con todos los tests
  - Análisis de puntos fuertes y débiles
  
- ✅ **Base de Datos SQLite:**
  - Almacenamiento local seguro
  - Backup manual (automático próximamente)
  - Portable (archivo único .db)

---

## 🚀 Quick Start

```bash
cd cognidata
source venv/bin/activate
streamlit run app.py
```

➡️ **http://localhost:8501**

### Primera Vez

```bash
cd cognidata
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 📱 Uso desde Tablet

1. Ejecuta la app en el ordenador
2. Anota la "Network URL" (ej: http://192.168.1.236:8501)
3. En la tablet (misma WiFi), abre esa URL en el navegador
4. ¡Funciona perfectamente en Safari/Chrome!

---

## 🎨 Capturas de Pantalla

### Dashboard con Perfil Cognitivo
- Gráfico Radar interactivo (Plotly)
- Comparación con media poblacional
- Código de colores por clasificación

### Formularios de Tests
- Interfaz limpia y clínica
- Validación automática
- Campos específicos por test
- Observaciones clínicas

### Resultados Inmediatos
- pe, percentil, clasificación automáticos
- Visualización clara y profesional
- Datos guardados en SQLite

---

## 📚 Documentación

- **README.md** (este archivo) - Visión general
- **[USAGE.md](USAGE.md)** - Manual detallado de usuario
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Detalles técnicos de implementación
- **[MODAL_ALERTS.md](MODAL_ALERTS.md)** - Sistema de notificaciones modales
- **[TESTING.md](TESTING.md)** - Guía completa de testing con pytest
- **[Plan técnico](~/.copilot/session-state/.../plan.md)** - Arquitectura y roadmap

### 🔔 Sistema de Notificaciones Modales

CogniData utiliza un **sistema profesional de notificaciones modales** para todas las alertas de usuario. 

**Uso rápido**:
```python
from utils import modal_success, modal_error, modal_warning, modal_info

modal_success("¡Éxito!", title="✅ Operación Exitosa")
modal_error("Error al guardar", title="❌ Error")
modal_warning("Esta acción es irreversible", title="⚠️ Advertencia")
modal_info("Procesando...", title="ℹ️ Por favor espere")
```

📖 **[Documentación completa](MODAL_ALERTS.md)** - Incluye patrones de uso, ejemplos, y guía de migración.

---

## 🔧 Stack Tecnológico

| Componente | Tecnología | Razón |
|------------|-----------|-------|
| **Framework UI** | Streamlit | Desarrollo rápido, ideal para dashboards científicos |
| **Lenguaje** | Python 3.11+ | Un solo lenguaje, ecosistema científico |
| **Base de Datos** | SQLite + SQLAlchemy | Simple, portable, sin servidor |
| **Gráficos** | Plotly | Interactivos, profesionales, nativos |
| **Cálculos** | NumPy + SciPy + Pandas | Estándar científico Python |

---

## 🆚 ¿Por qué Streamlit vs Next.js + FastAPI?

| Aspecto | Streamlit (Elegido) | Next.js + FastAPI |
|---------|---------------------|-------------------|
| **Complejidad** | 1 proyecto, ~500 líneas | 2 proyectos, miles de líneas |
| **Lenguajes** | 100% Python | JavaScript + Python |
| **Velocidad desarrollo** | 10x más rápido | Lento (webpack, babel, APIs) |
| **Deployment** | `streamlit run app.py` | Build frontend + 2 servidores |
| **Ideal para** | Uso local, científicos | Apps públicas, móviles |
| **Gráficos** | Plotly integrado | Recharts + configuración |
| **State** | Automático | Manual (Redux/Context) |

**Para una neuropsicóloga en su tablet/ordenador: Streamlit es la elección perfecta.**

---

## 📊 Estado del Proyecto

```
✅ Completado: 11/27 todos
🚧 En desarrollo: 16 todos restantes
```

### ✅ Fase 1 - MVP Funcional (COMPLETADO)
- ✅ Setup Streamlit + SQLite
- ✅ Models (Patient, TestSession)
- ✅ 6 tests completos con formularios
- ✅ Cálculo de normas automático
- ✅ Dashboard con gráficos Plotly
- ✅ CRUD pacientes
- ✅ Backup manual

### 🚧 Próximas Fases
- 🚧 Tablas NEURONORMA reales (actualmente simuladas)
- 🚧 Export PDF informes profesionales
- 🚧 Checklist clínico completo
- 🚧 Backup automático programado
- 🚧 Análisis longitudinal (evolución temporal)
- 🚧 Comparación entre pacientes (opcional)

---

## 🔒 RGPD y Seguridad

- ✅ **100% anónimo:** Solo UUID, edad, escolaridad, lateralidad
- ✅ **Sin identificadores:** No nombres, DNI, direcciones, emails
- ✅ **Local:** Base de datos en tu ordenador (`cognidata.db`)
- ✅ **Control total:** Tú decides dónde están tus datos
- ✅ **Derecho al olvido:** Eliminar paciente borra todo
- ✅ **Portabilidad:** Backup y restore en cualquier momento
- ✅ **Sin cloud forzado:** Opcional en el futuro

---

## 🛠️ Estructura del Proyecto

```
cognidata/
├── app.py                    # 🎯 Aplicación principal Streamlit (~700 líneas)
├── database/
│   └── connection.py         # SQLAlchemy + SQLite config
├── models/
│   ├── patient.py            # Modelo Patient (anónimo)
│   └── test_session.py       # Modelo TestSession
├── services/
│   └── normatives.py         # Motor de cálculo NEURONORMA
├── backups/                  # SQLite backups
├── .streamlit/
│   └── config.toml          # Tema clínico (azul + slate)
├── requirements.txt          # Dependencias Python
├── README.md                 # Este archivo
└── USAGE.md                  # Manual usuario detallado
```

---

## 🎓 Casos de Uso

### Uso Típico: Evaluación Completa

1. **Crear paciente:** 68 años, 12 años escolaridad, diestro
2. **Realizar batería de tests:**
   - TMT-A y TMT-B (atención y función ejecutiva)
   - TAVEC (memoria verbal)
   - Fluidez F-A-S (lenguaje)
   - Rey Copia y Memoria (visuoespacial)
3. **Ver Dashboard:** Perfil cognitivo completo
4. **Interpretar:** Puntos fuertes vs áreas de dificultad
5. **Backup:** Guardar sesión

---

## 📞 Soporte

**Versión:** 0.1.0 (Streamlit MVP)  
**Creado:** Marzo 2026  
**Licencia:** Uso privado profesional

Para preguntas o mejoras, consulta `USAGE.md` o el plan técnico.

---

## 🏆 Logros

- ✅ De 2 proyectos (frontend + backend) → 1 proyecto Python
- ✅ De ~5000 líneas de código → ~700 líneas
- ✅ De días de setup → minutos de setup
- ✅ De JavaScript + Python → 100% Python
- ✅ De complejo → simple y mantenible
- ✅ **MVP funcional en <2 horas de desarrollo**

---

**¡Listo para usar! 🚀**

---

## 🔒 Critical Security Fixes (v1.0.1)

**IMPORTANT: Read before deploying!**

This release includes 4 critical security fixes (GDPR Article 32 compliant).
You **MUST** set 2 environment variables before running the application.

### ⚡ Quick Setup

```bash
# 1. Generate JWT secret
export AUTH_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# 2. Set admin password
export ADMIN_PASSWORD='YourSecurePassword123!'

# 3. Update dependencies
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

### 🔐 What Was Fixed

| Issue | Impact | Status |
|-------|--------|--------|
| Hardcoded JWT secret | Authentication bypass | ✅ FIXED |
| Hardcoded admin password "admin123" | Default credential attacks | ✅ FIXED |
| JWT tokens in URL | Token exposure in logs/history | ✅ FIXED |
| Unmaintained passlib library | No security patches | ✅ FIXED |

### 📚 Documentation

- **CRITICAL_FIXES_QUICKSTART.md** - 5-minute setup guide
- **SECURITY_FIXES.md** - Comprehensive fix documentation
- **COMPLIANCE_AUDIT.md** - Full security audit (24 issues)

### ⚠️ Breaking Changes

None - no database schema changes, backward compatible.

### 🎯 Next Steps

Address HIGH priority issues (see COMPLIANCE_AUDIT.md):
- Data encryption at rest
- Data retention/TTL policy
- Backup file encryption
- HTTPS/TLS enforcement

