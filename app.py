"""
CogniData - Aplicación Neuropsicológica
Streamlit App para gestión de tests y cálculo de normas NEURONORMA
"""
import streamlit as st
from database.connection import init_db, SessionLocal
from models import Patient, TestSession
from services.normatives import calculator
from services.pdf_generator import pdf_generator
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="CogniData - Aplicación Neuropsicológica",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

st.title("🧠 CogniData - Aplicación Neuropsicológica")
st.markdown("### Gestión de tests y cálculo de normas NEURONORMA")

with st.sidebar:
    st.header("📋 Navegación")
    page = st.radio(
        "Selecciona una sección:",
        ["🏠 Inicio", "👥 Pacientes", "🧪 Tests", "📊 Dashboard", "⚙️ Configuración"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("Versión 0.1.0 - Streamlit")
    st.caption("100% Python - SQLite")

if page == "🏠 Inicio":
    col1, col2, col3 = st.columns(3)
    
    db = SessionLocal()
    total_patients = db.query(Patient).count()
    total_sessions = db.query(TestSession).count()
    db.close()
    
    with col1:
        st.metric("📊 Pacientes Totales", total_patients)
    with col2:
        st.metric("🧪 Tests Realizados", total_sessions)
    with col3:
        st.metric("📈 Tests Disponibles", "6")
    
    st.markdown("---")
    
    st.subheader("✅ Estado del Sistema")
    st.success("✓ Base de datos SQLite conectada")
    st.success("✓ Modelos inicializados")
    st.success("✓ Motor de cálculo normativo operativo")
    
    st.markdown("---")
    
    st.subheader("📚 Tests Disponibles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🔤 Trail Making Test (TMT)"):
            st.write("**TMT-A:** Atención sostenida y velocidad de procesamiento")
            st.write("**TMT-B:** Flexibilidad cognitiva y función ejecutiva")
        
        with st.expander("📝 TAVEC"):
            st.write("Test de Aprendizaje Verbal España-Complutense")
            st.write("Memoria episódica verbal y aprendizaje")
        
        with st.expander("💬 Fluidez Verbal (F-A-S)"):
            st.write("Fluidez fonológica con letras F, A, S")
    
    with col2:
        with st.expander("🎨 Figura de Rey - Copia"):
            st.write("Habilidades visuoconstructivas y planificación")
        
        with st.expander("🎨 Figura de Rey - Memoria"):
            st.write("Memoria visual diferida")
        
        with st.expander("📋 Observaciones Clínicas"):
            st.write("Checklist cualitativo + observaciones de proceso")

elif page == "👥 Pacientes":
    tab1, tab2 = st.tabs(["📋 Lista de Pacientes", "➕ Nuevo Paciente"])
    
    with tab1:
        st.subheader("Lista de Pacientes")
        
        db = SessionLocal()
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
        db.close()
        
        if patients:
            for patient in patients:
                with st.expander(f"ID: {patient.id[:8]}... | {patient.age} años | {patient.laterality}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Edad", f"{patient.age} años")
                    col2.metric("Escolaridad", f"{patient.education_years} años")
                    col3.metric("Lateralidad", patient.laterality.capitalize())
                    
                    st.caption(f"Creado: {patient.created_at.strftime('%d/%m/%Y %H:%M')}")
                    
                    if st.button(f"🗑️ Eliminar", key=f"del_{patient.id}"):
                        db = SessionLocal()
                        db.delete(patient)
                        db.commit()
                        db.close()
                        st.success("Paciente eliminado")
                        st.rerun()
        else:
            st.info("No hay pacientes registrados. Crea uno en la pestaña 'Nuevo Paciente'")
    
    with tab2:
        st.subheader("Registrar Nuevo Paciente")
        
        with st.form("new_patient_form"):
            age = st.number_input("Edad", min_value=18, max_value=100, value=65)
            education_years = st.number_input("Años de Escolaridad", min_value=0, max_value=25, value=12)
            laterality = st.selectbox("Lateralidad", ["diestro", "zurdo", "ambidextro"])
            
            submitted = st.form_submit_button("Guardar Paciente")
            
            if submitted:
                db = SessionLocal()
                new_patient = Patient(
                    age=age,
                    education_years=education_years,
                    laterality=laterality
                )
                db.add(new_patient)
                db.commit()
                patient_id = new_patient.id
                db.close()
                
                st.success(f"✅ Paciente creado con ID: {patient_id[:12]}...")
                st.balloons()

elif page == "🧪 Tests":
    st.subheader("Realizar Test Neuropsicológico")
    
    db = SessionLocal()
    patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
    db.close()
    
    if not patients:
        st.warning("⚠️ No hay pacientes registrados. Crea uno primero en la sección 'Pacientes'.")
    else:
        patient_options = {f"{p.id[:8]}... ({p.age} años)": p.id for p in patients}
        selected_patient_label = st.selectbox("Seleccionar Paciente", list(patient_options.keys()))
        selected_patient_id = patient_options[selected_patient_label]
        
        test_type = st.selectbox(
            "Tipo de Test",
            ["TMT-A", "TMT-B", "TAVEC", "Fluidez-FAS", "Rey-Copia", "Rey-Memoria"]
        )
        
        st.markdown("---")
        
        # TMT-A
        if test_type == "TMT-A":
            with st.form("tmt_a_form"):
                st.subheader("🔤 Trail Making Test - Parte A")
                st.caption("Atención sostenida y velocidad de procesamiento")
                
                col1, col2 = st.columns(2)
                with col1:
                    tiempo = st.number_input("Tiempo (segundos)", min_value=0.0, max_value=300.0, value=45.0, step=0.1)
                with col2:
                    errores = st.number_input("Errores", min_value=0, max_value=50, value=0)
                
                observaciones = st.text_area("Observaciones (opcional)", placeholder="Estrategias, comportamiento durante la prueba...")
                
                submitted = st.form_submit_button("💾 Calcular y Guardar")
                
                if submitted:
                    db = SessionLocal()
                    patient = db.query(Patient).filter_by(id=selected_patient_id).first()
                    
                    scores = calculator.calculate(
                        test_type="TMT-A",
                        raw_score=tiempo,
                        age=patient.age,
                        education_years=patient.education_years
                    )
                    
                    session = TestSession(
                        patient_id=selected_patient_id,
                        test_type=test_type
                    )
                    session.set_raw_data({"tiempo_segundos": tiempo, "errores": errores, "observaciones": observaciones})
                    session.set_calculated_scores(scores)
                    
                    db.add(session)
                    db.commit()
                    db.close()
                    
                    st.success("✅ Test TMT-A guardado exitosamente!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Puntuación Escalar (pe)", scores['puntuacion_escalar'])
                    col2.metric("Percentil", f"{scores['percentil']}%")
                    col3.metric("Clasificación", scores['clasificacion'])
                    
                    with st.expander("📊 Ver detalles completos"):
                        st.json(scores)
        
        # TMT-B
        elif test_type == "TMT-B":
            with st.form("tmt_b_form"):
                st.subheader("🔤🔢 Trail Making Test - Parte B")
                st.caption("Flexibilidad cognitiva y función ejecutiva")
                
                col1, col2 = st.columns(2)
                with col1:
                    tiempo = st.number_input("Tiempo (segundos)", min_value=0.0, max_value=600.0, value=120.0, step=0.1)
                with col2:
                    errores = st.number_input("Errores", min_value=0, max_value=50, value=0)
                
                observaciones = st.text_area("Observaciones (opcional)", placeholder="Dificultades de alternancia, perseveraciones...")
                
                submitted = st.form_submit_button("💾 Calcular y Guardar")
                
                if submitted:
                    db = SessionLocal()
                    patient = db.query(Patient).filter_by(id=selected_patient_id).first()
                    
                    scores = calculator.calculate(
                        test_type="TMT-B",
                        raw_score=tiempo,
                        age=patient.age,
                        education_years=patient.education_years
                    )
                    
                    session = TestSession(
                        patient_id=selected_patient_id,
                        test_type=test_type
                    )
                    session.set_raw_data({"tiempo_segundos": tiempo, "errores": errores, "observaciones": observaciones})
                    session.set_calculated_scores(scores)
                    
                    db.add(session)
                    db.commit()
                    db.close()
                    
                    st.success("✅ Test TMT-B guardado exitosamente!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Puntuación Escalar (pe)", scores['puntuacion_escalar'])
                    col2.metric("Percentil", f"{scores['percentil']}%")
                    col3.metric("Clasificación", scores['clasificacion'])
                    
                    with st.expander("📊 Ver detalles completos"):
                        st.json(scores)
        
        # TAVEC
        elif test_type == "TAVEC":
            with st.form("tavec_form"):
                st.subheader("📝 TAVEC - Test de Aprendizaje Verbal España-Complutense")
                st.caption("Memoria episódica verbal y aprendizaje")
                
                st.markdown("**Lista A - Ensayos 1 a 5**")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    ensayo1 = st.number_input("Ensayo 1", 0, 16, 8, key="e1")
                with col2:
                    ensayo2 = st.number_input("Ensayo 2", 0, 16, 10, key="e2")
                with col3:
                    ensayo3 = st.number_input("Ensayo 3", 0, 16, 12, key="e3")
                with col4:
                    ensayo4 = st.number_input("Ensayo 4", 0, 16, 13, key="e4")
                with col5:
                    ensayo5 = st.number_input("Ensayo 5", 0, 16, 14, key="e5")
                
                total_a = ensayo1 + ensayo2 + ensayo3 + ensayo4 + ensayo5
                st.info(f"**Total Lista A (ensayos 1-5):** {total_a} palabras")
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    lista_b = st.number_input("Lista B (Interferencia)", 0, 16, 6)
                    recuerdo_inmediato = st.number_input("Recuerdo Inmediato Lista A", 0, 16, 12)
                with col2:
                    recuerdo_diferido = st.number_input("Recuerdo Diferido (20 min)", 0, 16, 11)
                    reconocimiento = st.number_input("Reconocimiento", 0, 16, 15)
                
                st.markdown("**Errores**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    intrusiones = st.number_input("Intrusiones", 0, 50, 0)
                with col2:
                    perseveraciones = st.number_input("Perseveraciones", 0, 50, 0)
                with col3:
                    falsos_positivos = st.number_input("Falsos Positivos (Reconoc.)", 0, 50, 0)
                
                observaciones = st.text_area("Observaciones", placeholder="Estrategias de codificación, curva de aprendizaje...")
                
                submitted = st.form_submit_button("💾 Calcular y Guardar")
                
                if submitted:
                    db = SessionLocal()
                    patient = db.query(Patient).filter_by(id=selected_patient_id).first()
                    
                    # Usar total Lista A como puntuación principal
                    scores = calculator.calculate(
                        test_type="TAVEC",
                        raw_score=total_a,
                        age=patient.age,
                        education_years=patient.education_years
                    )
                    
                    raw_data = {
                        "ensayos": [ensayo1, ensayo2, ensayo3, ensayo4, ensayo5],
                        "total_lista_a": total_a,
                        "lista_b": lista_b,
                        "recuerdo_inmediato": recuerdo_inmediato,
                        "recuerdo_diferido": recuerdo_diferido,
                        "reconocimiento": reconocimiento,
                        "intrusiones": intrusiones,
                        "perseveraciones": perseveraciones,
                        "falsos_positivos": falsos_positivos,
                        "observaciones": observaciones
                    }
                    
                    session = TestSession(
                        patient_id=selected_patient_id,
                        test_type=test_type
                    )
                    session.set_raw_data(raw_data)
                    session.set_calculated_scores(scores)
                    
                    db.add(session)
                    db.commit()
                    db.close()
                    
                    st.success("✅ Test TAVEC guardado exitosamente!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Puntuación Escalar (pe)", scores['puntuacion_escalar'])
                    col2.metric("Percentil", f"{scores['percentil']}%")
                    col3.metric("Clasificación", scores['clasificacion'])
                    
                    with st.expander("📊 Ver detalles completos"):
                        st.json(scores)
        
        # Fluidez Verbal F-A-S
        elif test_type == "Fluidez-FAS":
            with st.form("fluidez_form"):
                st.subheader("💬 Test de Fluidez Verbal Fonológica (F-A-S)")
                st.caption("60 segundos por letra - Función ejecutiva y acceso léxico")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    letra_f = st.number_input("Letra F", 0, 50, 14)
                with col2:
                    letra_a = st.number_input("Letra A", 0, 50, 12)
                with col3:
                    letra_s = st.number_input("Letra S", 0, 50, 13)
                
                total_fas = letra_f + letra_a + letra_s
                st.info(f"**Total F-A-S:** {total_fas} palabras")
                
                st.markdown("**Errores**")
                col1, col2 = st.columns(2)
                with col1:
                    perseveraciones = st.number_input("Perseveraciones", 0, 20, 0)
                with col2:
                    intrusiones = st.number_input("Intrusiones/Errores", 0, 20, 0)
                
                observaciones = st.text_area("Observaciones", placeholder="Estrategias de búsqueda, clustering semántico...")
                
                submitted = st.form_submit_button("💾 Calcular y Guardar")
                
                if submitted:
                    db = SessionLocal()
                    patient = db.query(Patient).filter_by(id=selected_patient_id).first()
                    
                    scores = calculator.calculate(
                        test_type="Fluidez-FAS",
                        raw_score=total_fas,
                        age=patient.age,
                        education_years=patient.education_years
                    )
                    
                    raw_data = {
                        "letra_f": letra_f,
                        "letra_a": letra_a,
                        "letra_s": letra_s,
                        "total": total_fas,
                        "perseveraciones": perseveraciones,
                        "intrusiones": intrusiones,
                        "observaciones": observaciones
                    }
                    
                    session = TestSession(
                        patient_id=selected_patient_id,
                        test_type=test_type
                    )
                    session.set_raw_data(raw_data)
                    session.set_calculated_scores(scores)
                    
                    db.add(session)
                    db.commit()
                    db.close()
                    
                    st.success("✅ Test de Fluidez Verbal guardado exitosamente!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Puntuación Escalar (pe)", scores['puntuacion_escalar'])
                    col2.metric("Percentil", f"{scores['percentil']}%")
                    col3.metric("Clasificación", scores['clasificacion'])
                    
                    with st.expander("📊 Ver detalles completos"):
                        st.json(scores)
        
        # Figura de Rey - Copia
        elif test_type == "Rey-Copia":
            with st.form("rey_copia_form"):
                st.subheader("🎨 Figura Compleja de Rey - Copia")
                st.caption("Habilidades visuoconstructivas y planificación")
                
                col1, col2 = st.columns(2)
                with col1:
                    puntuacion = st.number_input("Puntuación (0-36)", 0.0, 36.0, 28.0, 0.5)
                with col2:
                    tiempo = st.number_input("Tiempo (segundos)", 0, 900, 180, 5)
                
                tipo_copia = st.selectbox(
                    "Tipo de Copia (Osterrieth)",
                    ["Tipo I - Constructivo", "Tipo II - Detalles importantes", 
                     "Tipo III - Contorno general", "Tipo IV - Yuxtaposición", 
                     "Tipo V - Detalles sin estructura", "Tipo VI - Sustitución", 
                     "Tipo VII - Garabateo"]
                )
                
                observaciones = st.text_area("Observaciones", placeholder="Estrategia de copia, precisión, organización espacial...")
                
                submitted = st.form_submit_button("💾 Calcular y Guardar")
                
                if submitted:
                    db = SessionLocal()
                    patient = db.query(Patient).filter_by(id=selected_patient_id).first()
                    
                    scores = calculator.calculate(
                        test_type="Rey-Copia",
                        raw_score=puntuacion,
                        age=patient.age,
                        education_years=patient.education_years
                    )
                    
                    raw_data = {
                        "puntuacion_bruta": puntuacion,
                        "tiempo_segundos": tiempo,
                        "tipo_copia": tipo_copia,
                        "observaciones": observaciones
                    }
                    
                    session = TestSession(
                        patient_id=selected_patient_id,
                        test_type=test_type
                    )
                    session.set_raw_data(raw_data)
                    session.set_calculated_scores(scores)
                    
                    db.add(session)
                    db.commit()
                    db.close()
                    
                    st.success("✅ Test Figura de Rey (Copia) guardado exitosamente!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Puntuación Escalar (pe)", scores['puntuacion_escalar'])
                    col2.metric("Percentil", f"{scores['percentil']}%")
                    col3.metric("Clasificación", scores['clasificacion'])
                    
                    with st.expander("📊 Ver detalles completos"):
                        st.json(scores)
        
        # Figura de Rey - Memoria
        elif test_type == "Rey-Memoria":
            with st.form("rey_memoria_form"):
                st.subheader("🎨 Figura Compleja de Rey - Memoria")
                st.caption("Memoria visual diferida (típicamente después de 3-30 minutos)")
                
                col1, col2 = st.columns(2)
                with col1:
                    puntuacion = st.number_input("Puntuación (0-36)", 0.0, 36.0, 18.0, 0.5)
                with col2:
                    tiempo_demora = st.number_input("Tiempo de Demora (minutos)", 3, 60, 20, 1)
                
                observaciones = st.text_area("Observaciones", placeholder="Elementos recordados, distorsiones, estrategias de recuperación...")
                
                submitted = st.form_submit_button("💾 Calcular y Guardar")
                
                if submitted:
                    db = SessionLocal()
                    patient = db.query(Patient).filter_by(id=selected_patient_id).first()
                    
                    scores = calculator.calculate(
                        test_type="Rey-Memoria",
                        raw_score=puntuacion,
                        age=patient.age,
                        education_years=patient.education_years
                    )
                    
                    raw_data = {
                        "puntuacion_bruta": puntuacion,
                        "tiempo_demora_minutos": tiempo_demora,
                        "observaciones": observaciones
                    }
                    
                    session = TestSession(
                        patient_id=selected_patient_id,
                        test_type=test_type
                    )
                    session.set_raw_data(raw_data)
                    session.set_calculated_scores(scores)
                    
                    db.add(session)
                    db.commit()
                    db.close()
                    
                    st.success("✅ Test Figura de Rey (Memoria) guardado exitosamente!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Puntuación Escalar (pe)", scores['puntuacion_escalar'])
                    col2.metric("Percentil", f"{scores['percentil']}%")
                    col3.metric("Clasificación", scores['clasificacion'])
                    
                    with st.expander("📊 Ver detalles completos"):
                        st.json(scores)

elif page == "📊 Dashboard":
    st.subheader("📊 Panel de Análisis y Perfil Cognitivo")
    
    # Seleccionar paciente
    db = SessionLocal()
    patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
    
    if not patients:
        db.close()
        st.warning("⚠️ No hay pacientes registrados. Crea uno primero en la sección 'Pacientes'.")
    else:
        patient_options = {f"{p.id[:8]}... ({p.age} años, {p.education_years} años escolaridad)": p.id for p in patients}
        selected_patient_label = st.selectbox("Seleccionar Paciente para Análisis", list(patient_options.keys()))
        selected_patient_id = patient_options[selected_patient_label]
        
        # Obtener sesiones del paciente
        sessions = db.query(TestSession).filter_by(patient_id=selected_patient_id).order_by(TestSession.date.desc()).all()
        patient = db.query(Patient).filter_by(id=selected_patient_id).first()
        db.close()
        
        if not sessions:
            st.info(f"👤 Paciente seleccionado: {patient.age} años, {patient.education_years} años de escolaridad")
            st.warning("Este paciente no tiene tests realizados aún. Ve a la sección 'Tests' para realizar evaluaciones.")
        else:
            # Información del paciente
            col1, col2, col3 = st.columns(3)
            col1.metric("👤 Edad", f"{patient.age} años")
            col2.metric("🎓 Escolaridad", f"{patient.education_years} años")
            col3.metric("🧪 Tests Realizados", len(sessions))
            
            st.markdown("---")
            
            # Preparar datos para gráfico
            test_names = []
            pe_scores = []
            percentiles = []
            clasificaciones = []
            
            for session in sessions:
                scores = session.get_calculated_scores()
                if scores:
                    test_names.append(session.test_type)
                    pe_scores.append(scores.get('puntuacion_escalar', 10))
                    percentiles.append(scores.get('percentil', 50))
                    clasificaciones.append(scores.get('clasificacion', 'N/A'))
            
            if test_names:
                # Gráfico Radar - Perfil Cognitivo
                st.subheader("🎯 Perfil Cognitivo - Puntuaciones Escalares")
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=pe_scores,
                    theta=test_names,
                    fill='toself',
                    name='Perfil del Paciente',
                    line=dict(color='#2563eb', width=2),
                    marker=dict(size=8, color='#2563eb')
                ))
                
                # Línea de referencia (pe=10 es la media)
                fig.add_trace(go.Scatterpolar(
                    r=[10] * len(test_names),
                    theta=test_names,
                    fill=None,
                    name='Media Poblacional (pe=10)',
                    line=dict(color='#10b981', width=2, dash='dash'),
                    marker=dict(size=0)
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 19],
                            tickmode='linear',
                            tick0=0,
                            dtick=5,
                            showline=True,
                            gridcolor='#e5e7eb'
                        ),
                        angularaxis=dict(
                            gridcolor='#e5e7eb'
                        )
                    ),
                    showlegend=True,
                    height=500,
                    title=dict(
                        text="Puntuaciones Escalares (pe) - Escala: 1-19, Media: 10, DE: 3",
                        x=0.5,
                        xanchor='center'
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Gráfico de Barras - Percentiles
                st.subheader("📊 Percentiles por Test")
                
                fig_bar = go.Figure()
                
                # Colores según clasificación
                colors = []
                for clasificacion in clasificaciones:
                    if clasificacion == "Superior":
                        colors.append('#10b981')  # Verde
                    elif clasificacion == "Normal":
                        colors.append('#3b82f6')  # Azul
                    elif clasificacion == "Limítrofe":
                        colors.append('#f59e0b')  # Amarillo
                    else:  # Deficitario
                        colors.append('#ef4444')  # Rojo
                
                fig_bar.add_trace(go.Bar(
                    x=test_names,
                    y=percentiles,
                    text=[f"{p}%" for p in percentiles],
                    textposition='outside',
                    marker=dict(color=colors),
                    name='Percentil'
                ))
                
                # Líneas de referencia
                fig_bar.add_hline(y=75, line_dash="dash", line_color="#10b981", 
                                  annotation_text="Superior (P75)", annotation_position="right")
                fig_bar.add_hline(y=25, line_dash="dash", line_color="#3b82f6", 
                                  annotation_text="Normal (P25)", annotation_position="right")
                fig_bar.add_hline(y=10, line_dash="dash", line_color="#f59e0b", 
                                  annotation_text="Limítrofe (P10)", annotation_position="right")
                
                fig_bar.update_layout(
                    yaxis=dict(title="Percentil", range=[0, 100]),
                    xaxis=dict(title="Test"),
                    height=400,
                    showlegend=False,
                    title="Distribución de Percentiles"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                st.markdown("---")
                
                # Tabla resumen
                st.subheader("📋 Resumen de Resultados")
                
                import pandas as pd
                df_results = pd.DataFrame({
                    'Test': test_names,
                    'Fecha': [s.date.strftime('%d/%m/%Y %H:%M') for s in sessions],
                    'pe': pe_scores,
                    'Percentil': [f"{p}%" for p in percentiles],
                    'Clasificación': clasificaciones
                })
                
                st.dataframe(df_results, use_container_width=True, hide_index=True)
                
                # Interpretación
                st.markdown("---")
                st.subheader("💡 Interpretación")
                
                # Calcular media compuesta
                mean_pe = sum(pe_scores) / len(pe_scores)
                mean_percentil = sum(percentiles) / len(percentiles)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Media de Puntuación Escalar", f"{mean_pe:.1f}")
                    if mean_pe >= 13:
                        st.success("🟢 Rendimiento global superior a la media")
                    elif mean_pe >= 7:
                        st.info("🔵 Rendimiento global dentro de la normalidad")
                    elif mean_pe >= 4:
                        st.warning("🟡 Rendimiento global en rango limítrofe")
                    else:
                        st.error("🔴 Rendimiento global por debajo de lo esperado")
                
                with col2:
                    st.metric("Media de Percentil", f"{mean_percentil:.1f}%")
                    st.caption("Comparación con población normativa según edad y escolaridad")
                
                # Puntos fuertes y débiles
                if len(pe_scores) > 1:
                    max_idx = pe_scores.index(max(pe_scores))
                    min_idx = pe_scores.index(min(pe_scores))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(f"**💪 Punto Fuerte:** {test_names[max_idx]} (pe={pe_scores[max_idx]})")
                    with col2:
                        st.warning(f"**⚠️ Área de Dificultad:** {test_names[min_idx]} (pe={pe_scores[min_idx]})")
                
                # Exportar PDF
                st.markdown("---")
                st.subheader("📄 Exportar Informe")
                
                if st.button("📥 Generar Informe PDF", type="primary"):
                    with st.spinner("Generando informe PDF..."):
                        try:
                            # Preparar datos del paciente
                            patient_dict = {
                                'id': patient.id,
                                'age': patient.age,
                                'education_years': patient.education_years,
                                'laterality': patient.laterality
                            }
                            
                            # Preparar datos de sesiones
                            sessions_data = []
                            for session in sessions:
                                session_dict = {
                                    'test_type': session.test_type,
                                    'date': session.date,
                                    'raw_data': session.get_raw_data(),
                                    'calculated_scores': session.get_calculated_scores(),
                                    'qualitative_data': session.get_qualitative_data()
                                }
                                sessions_data.append(session_dict)
                            
                            # Generar PDF
                            pdf_path = pdf_generator.generate_report(
                                patient_data=patient_dict,
                                test_sessions=sessions_data
                            )
                            
                            # Leer archivo PDF
                            with open(pdf_path, 'rb') as pdf_file:
                                pdf_bytes = pdf_file.read()
                            
                            # Botón de descarga
                            st.success(f"✅ Informe generado exitosamente")
                            st.download_button(
                                label="⬇️ Descargar PDF",
                                data=pdf_bytes,
                                file_name=os.path.basename(pdf_path),
                                mime='application/pdf'
                            )
                            
                        except Exception as e:
                            st.error(f"❌ Error al generar PDF: {str(e)}")


elif page == "⚙️ Configuración":
    st.subheader("Configuración y Backup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💾 Backup de Datos")
        if st.button("Crear Backup Ahora"):
            import shutil
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2("cognidata.db", f"backups/cognidata_{timestamp}.db")
            st.success(f"✅ Backup creado: cognidata_{timestamp}.db")
    
    with col2:
        st.markdown("### 📤 Exportar Datos")
        if st.button("Exportar JSON"):
            st.info("🚧 Funcionalidad en desarrollo")
    
    st.markdown("---")
    st.markdown("### ℹ️ Información del Sistema")
    st.code("""Base de datos: SQLite (cognidata.db)
Versión: 0.1.0
Framework: Streamlit
Python: 3.11+""")
