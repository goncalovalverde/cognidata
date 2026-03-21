# Guía de Uso - CogniData

## 🚀 Inicio Rápido

### Ejecutar la aplicación

```bash
cd cognidata
source venv/bin/activate
streamlit run app.py
```

Abre tu navegador en: **http://localhost:8501**

---

## 📖 Manual de Usuario

### 1. Crear un Paciente

1. Ve a **👥 Pacientes** → **➕ Nuevo Paciente**
2. Introduce:
   - Edad (18-100 años)
   - Años de Escolaridad (0-25)
   - Lateralidad (diestro/zurdo/ambidextro)
3. Click **Guardar Paciente**
4. Se genera automáticamente un ID anónimo (UUID)

### 2. Realizar un Test

1. Ve a **🧪 Tests**
2. Selecciona el paciente
3. Selecciona el tipo de test
4. Completa el formulario específico:

#### TMT-A (Trail Making Test - Parte A)
- **Tiempo:** Segundos que tardó el paciente
- **Errores:** Número de errores cometidos
- **Observaciones:** Estrategias, comportamiento

#### TMT-B (Trail Making Test - Parte B)
- **Tiempo:** Segundos (generalmente más que TMT-A)
- **Errores:** Errores de alternancia
- **Observaciones:** Dificultades de flexibilidad cognitiva

#### TAVEC
- **Ensayos 1-5:** Palabras recordadas en cada ensayo (0-16)
- **Lista B:** Interferencia (0-16)
- **Recuerdo Inmediato:** Post-interferencia (0-16)
- **Recuerdo Diferido:** A los 20 minutos (0-16)
- **Reconocimiento:** Total de items reconocidos (0-16)
- **Errores:** Intrusiones, perseveraciones, falsos positivos
- **Observaciones:** Curva de aprendizaje, estrategias

#### Fluidez Verbal F-A-S
- **Letra F:** Palabras generadas en 60s
- **Letra A:** Palabras generadas en 60s
- **Letra S:** Palabras generadas en 60s
- **Total:** Suma automática
- **Errores:** Perseveraciones e intrusiones
- **Observaciones:** Estrategias de búsqueda

#### Figura de Rey - Copia
- **Puntuación:** 0-36 puntos según criterios
- **Tiempo:** Segundos de ejecución
- **Tipo de Copia:** Clasificación Osterrieth (Tipo I-VII)
- **Observaciones:** Estrategia, organización espacial

#### Figura de Rey - Memoria
- **Puntuación:** 0-36 puntos
- **Tiempo de Demora:** Minutos transcurridos (típicamente 3-30)
- **Observaciones:** Elementos recordados, distorsiones

5. Click **💾 Calcular y Guardar**
6. El sistema calcula automáticamente:
   - **Puntuación Escalar (pe):** Escala 1-19, media=10, DE=3
   - **Percentil:** Comparación con población normativa
   - **Clasificación:** Superior/Normal/Limítrofe/Deficitario

### 3. Ver Dashboard

1. Ve a **📊 Dashboard**
2. Selecciona el paciente
3. Visualiza:
   - **Gráfico Radar:** Perfil cognitivo multidimensional
   - **Gráfico de Barras:** Percentiles con código de colores
   - **Tabla Resumen:** Todos los tests y fechas
   - **Interpretación:** Media global y puntos fuertes/débiles

**Código de Colores:**
- 🟢 Verde: Superior (percentil ≥75)
- 🔵 Azul: Normal (25-74)
- 🟡 Amarillo: Limítrofe (10-24)
- 🔴 Rojo: Deficitario (<10)

### 4. Gestionar Pacientes

1. Ve a **👥 Pacientes** → **📋 Lista de Pacientes**
2. Expande cada paciente para ver detalles
3. Click **🗑️ Eliminar** para borrar (cumple RGPD - derecho al olvido)
   - ⚠️ Esto eliminará también todos los tests asociados

### 5. Backup de Datos

1. Ve a **⚙️ Configuración**
2. Click **Crear Backup Ahora**
3. Se guarda en: `backups/cognidata_YYYYMMDD_HHMMSS.db`
4. Copia manual del archivo para backup externo

---

## 🎯 Interpretación de Resultados

### Puntuación Escalar (pe)
- **Escala:** 1-19
- **Media:** 10
- **Desviación Estándar:** 3
- **Rangos:**
  - 13-19: Superior
  - 7-12: Normal
  - 4-6: Limítrofe
  - 1-3: Deficitario

### Percentiles
- **P75+:** Superior (25% superior de la población)
- **P25-P74:** Normal (50% medio)
- **P10-P24:** Limítrofe (requiere seguimiento)
- **<P10:** Deficitario (intervención recomendada)

### Perfil Cognitivo
El gráfico radar muestra:
- **Picos:** Áreas de fortaleza cognitiva
- **Valles:** Áreas de dificultad
- **Línea verde discontinua:** Media poblacional (pe=10)
- **Distancia de la media:** Indica desviación del perfil típico

---

## 📱 Uso desde Tablet

1. Asegúrate de que el ordenador y la tablet están en la misma red WiFi
2. En el ordenador, ejecuta: `streamlit run app.py`
3. Anota la "Network URL" que aparece (ej: http://192.168.1.236:8501)
4. En la tablet, abre el navegador y accede a esa URL
5. Funciona igual que en el ordenador

---

## 🔒 Privacidad y RGPD

- ✅ **Datos anónimos:** Solo UUID, edad, escolaridad, lateralidad
- ✅ **Sin datos personales:** No se guardan nombres, DNI, emails
- ✅ **Base de datos local:** `cognidata.db` en tu ordenador
- ✅ **Derecho al olvido:** Eliminar paciente borra todos sus datos
- ✅ **Portabilidad:** Exportar/importar datos (próximamente)
- ✅ **Control total:** Tú controlas dónde están los datos

---

## ⚠️ Limitaciones Actuales

- **Normas NEURONORMA:** Actualmente usa cálculos simulados. Las tablas reales NEURONORMA se añadirán próximamente.
- **Export PDF:** En desarrollo
- **Observaciones clínicas:** Checklist completo en desarrollo
- **Backup automático:** Solo manual por ahora

---

## 🆘 Solución de Problemas

### La app no arranca
```bash
# Verifica que el entorno virtual esté activado
source venv/bin/activate

# Reinstala dependencias
pip install -r requirements.txt

# Ejecuta de nuevo
streamlit run app.py
```

### Error de base de datos
```bash
# Elimina y reinicia la base de datos
rm cognidata.db
streamlit run app.py
```

### No veo mi paciente/test
```bash
# Refresca la página del navegador
# Streamlit recarga automáticamente los datos
```

---

## 📞 Contacto

Para soporte o preguntas: [Tu contacto aquí]

**Versión:** 0.1.0 (Streamlit)
