"""
Tests page - Neuropsychological test administration
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from PIL import Image
from database.connection import SessionLocal
from models import Patient, TestSession
from services.normatives import calculator
from services.audit import audit_service
from services.patient_protocol_service import patient_protocol_service
from components.design_components import alert, header


def render():
    """Render the tests page"""
    header("<i class='ph ph-flask'></i> Realizar Test Neuropsicológico", "")

    db = SessionLocal()
    try:
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()

        if not patients:
            alert(
                "No hay pacientes registrados. Crea uno primero en la sección 'Pacientes'.",
                alert_type="warning"
            )
        else:
            patient_options = {f"{p.id[:8]}... ({p.age} años)": p.id for p in patients}
            selected_patient_label = st.selectbox(
                "Seleccionar Paciente", list(patient_options.keys())
            )
            selected_patient_id = patient_options[selected_patient_label]

            # Show protocol information if available
            assignments = patient_protocol_service.get_patient_protocols(selected_patient_id)
            if assignments:
                col1, col2, col3 = st.columns(3)
                for i, assignment in enumerate(assignments):
                    if i >= 3:  # Show max 3 protocols
                        break
                    protocol = assignment.protocol
                    completion = patient_protocol_service.get_protocol_completion_status(
                        selected_patient_id, protocol.id
                    )
                    with col1 if i == 0 else (col2 if i == 1 else col3):
                        st.metric(
                            f"📑 {protocol.name[:20]}",
                            f"{completion['percentage']}%",
                            f"{completion['completed_tests']}/{completion['total_tests']}"
                        )
                
                if len(assignments) > 3:
                    st.caption(f"... y {len(assignments) - 3} más protocolos")
                
                st.markdown("---")

            test_type = st.selectbox(
                "Tipo de Test",
                [
                    "TMT-A", "TMT-B", "TAVEC", "Fluidez-FAS", "Fluidez-Semántica",
                    "Rey-Copia", "Rey-Memoria", "Toulouse-Pieron", "Torre de Londres",
                    "DIVA-5", "BRIEF-A", "WAIS-IV", "Dígitos", "Test d2-R", "FDT",
                    "BADS-Zoo", "BADS-Llave", "FCSRT", "Perfil Sensorial"
                ],
            )

            st.markdown("---")

            if test_type == "TMT-A":
                _render_tmt_a_form(selected_patient_id)
            elif test_type == "TMT-B":
                _render_tmt_b_form(selected_patient_id)
            elif test_type == "TAVEC":
                _render_tavec_form(selected_patient_id)
            elif test_type == "Fluidez-FAS":
                _render_fluidez_form(selected_patient_id)
            elif test_type == "Fluidez-Semántica":
                _render_fluidez_semantic_form(selected_patient_id)
            elif test_type == "Rey-Copia":
                _render_rey_copia_form(selected_patient_id)
            elif test_type == "Rey-Memoria":
                _render_rey_memoria_form(selected_patient_id)
            elif test_type == "Toulouse-Pieron":
                _render_toulouse_pieron_form(selected_patient_id)
            elif test_type == "Torre de Londres":
                _render_torre_de_londres_form(selected_patient_id)
            elif test_type == "DIVA-5":
                _render_diva5_form(selected_patient_id)
            elif test_type == "BRIEF-A":
                _render_brief_a_form(selected_patient_id)
            elif test_type == "WAIS-IV":
                _render_wais_iv_form(selected_patient_id)
            elif test_type == "Dígitos":
                _render_digitos_form(selected_patient_id)
            elif test_type == "Test d2-R":
                _render_d2r_form(selected_patient_id)
            elif test_type == "FDT":
                _render_fdt_form(selected_patient_id)
            elif test_type == "BADS-Zoo":
                _render_bads_zoo_form(selected_patient_id)
            elif test_type == "BADS-Llave":
                _render_bads_llave_form(selected_patient_id)
            elif test_type == "FCSRT":
                _render_fcsrt_form(selected_patient_id)
            elif test_type == "Perfil Sensorial":
                _render_perfil_sensorial_form(selected_patient_id)
    finally:
        db.close()


def _get_patient_data(patient_id: str) -> dict:
    """Get patient data by ID"""
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter_by(id=patient_id).first()
        if patient:
            return {
                "id": patient.id,
                "age": patient.age,
                "education_years": patient.education_years,
                "laterality": patient.laterality,
            }
        return None
    finally:
        db.close()


def _save_test_session(
    patient_id: str, test_type: str, raw_data: dict, scores: dict
) -> str:
    """Save a test session and return its ID"""
    db = SessionLocal()
    try:
        session = TestSession(patient_id=patient_id, test_type=test_type)
        
        # Try to find an active protocol for this test
        assignments = patient_protocol_service.get_patient_protocols(patient_id)
        for assignment in assignments:
            protocol = assignment.protocol
            # Check if this test type is in the protocol
            test_types = [t.test_type for t in protocol.tests]
            if test_type in test_types and assignment.status in ["pending", "in_progress"]:
                session.protocol_id = protocol.id
                # Update status to in_progress if it was pending
                if assignment.status == "pending":
                    patient_protocol_service.update_protocol_status(
                        patient_id, protocol.id, "in_progress"
                    )
                break
        
        session.set_raw_data(raw_data)
        session.set_calculated_scores(scores)
        db.add(session)
        db.commit()
        session_id = str(session.id)
    finally:
        db.close()

    audit_service.log_test_create(session_id, patient_id, test_type, scores)
    return session_id


def _display_scores(scores: dict):
    """Display test scores in a nice format"""
    col1, col2, col3 = st.columns(3)
    col1.metric("Puntuación Escalar (pe)", scores["puntuacion_escalar"])
    col2.metric("Percentil", f"{scores['percentil']}%")
    col3.metric("Clasificación", scores["clasificacion"])

    with st.expander("📊 Ver detalles completos"):
        st.json(scores)


def _render_tmt_a_form(patient_id: str):
    """Render TMT-A test form"""
    with st.form("tmt_a_form"):
        st.subheader("🔤 Trail Making Test - Parte A")
        st.caption("Atención sostenida y velocidad de procesamiento")

        col1, col2 = st.columns(2)
        with col1:
            tiempo = st.number_input(
                "Tiempo (segundos)",
                min_value=0.0,
                max_value=300.0,
                value=45.0,
                step=0.1,
            )
        with col2:
            errores = st.number_input("Errores", min_value=0, max_value=50, value=0)

        observaciones = st.text_area(
            "Observaciones (opcional)",
            placeholder="Estrategias, comportamiento durante la prueba...",
        )

        submitted = st.form_submit_button("💾 Calcular y Guardar")

        if submitted:
            patient = _get_patient_data(patient_id)
            scores = calculator.calculate(
                test_type="TMT-A",
                raw_score=tiempo,
                age=patient["age"],
                education_years=patient["education_years"],
            )

            raw_data = {
                "tiempo_segundos": tiempo,
                "errores": errores,
                "observaciones": observaciones,
            }

            _save_test_session(patient_id, "TMT-A", raw_data, scores)

            alert("Test TMT-A guardado exitosamente!", alert_type="success")
            _display_scores(scores)


def _render_tmt_b_form(patient_id: str):
    """Render TMT-B test form"""
    with st.form("tmt_b_form"):
        st.subheader("🔤🔢 Trail Making Test - Parte B")
        st.caption("Flexibilidad cognitiva y función ejecutiva")

        col1, col2 = st.columns(2)
        with col1:
            tiempo = st.number_input(
                "Tiempo (segundos)",
                min_value=0.0,
                max_value=600.0,
                value=120.0,
                step=0.1,
            )
        with col2:
            errores = st.number_input("Errores", min_value=0, max_value=50, value=0)

        observaciones = st.text_area(
            "Observaciones (opcional)",
            placeholder="Dificultades de alternancia, perseveraciones...",
        )

        submitted = st.form_submit_button("💾 Calcular y Guardar")

        if submitted:
            patient = _get_patient_data(patient_id)
            scores = calculator.calculate(
                test_type="TMT-B",
                raw_score=tiempo,
                age=patient["age"],
                education_years=patient["education_years"],
            )

            raw_data = {
                "tiempo_segundos": tiempo,
                "errores": errores,
                "observaciones": observaciones,
            }

            _save_test_session(patient_id, "TMT-B", raw_data, scores)

            alert("Test TMT-B guardado exitosamente!", alert_type="success")
            _display_scores(scores)


def _render_tavec_form(patient_id: str):
    """Render TAVEC test form"""
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
        alert(f"**Total Lista A (ensayos 1-5):** {total_a} palabras", alert_type="info")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            lista_b = st.number_input("Lista B (Interferencia)", 0, 16, 6)
            recuerdo_inmediato = st.number_input(
                "Recuerdo Inmediato Lista A", 0, 16, 12
            )
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

        observaciones = st.text_area(
            "Observaciones",
            placeholder="Estrategias de codificación, curva de aprendizaje...",
        )

        submitted = st.form_submit_button("💾 Calcular y Guardar")

        if submitted:
            patient = _get_patient_data(patient_id)
            scores = calculator.calculate(
                test_type="TAVEC",
                raw_score=total_a,
                age=patient["age"],
                education_years=patient["education_years"],
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
                "observaciones": observaciones,
            }

            _save_test_session(patient_id, "TAVEC", raw_data, scores)

            alert("Test TAVEC guardado exitosamente!", alert_type="success")
            _display_scores(scores)


def _render_fluidez_form(patient_id: str):
    """Render Fluidez Verbal F-A-S test form"""
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
        alert(f"**Total F-A-S:** {total_fas} palabras", alert_type="info")

        st.markdown("**Errores**")
        col1, col2 = st.columns(2)
        with col1:
            perseveraciones = st.number_input("Perseveraciones", 0, 20, 0)
        with col2:
            intrusiones = st.number_input("Intrusiones/Errores", 0, 20, 0)

        observaciones = st.text_area(
            "Observaciones",
            placeholder="Estrategias de búsqueda, clustering semántico...",
        )

        submitted = st.form_submit_button("💾 Calcular y Guardar")

        if submitted:
            patient = _get_patient_data(patient_id)
            scores = calculator.calculate(
                test_type="Fluidez-FAS",
                raw_score=total_fas,
                age=patient["age"],
                education_years=patient["education_years"],
            )

            raw_data = {
                "letra_f": letra_f,
                "letra_a": letra_a,
                "letra_s": letra_s,
                "total": total_fas,
                "perseveraciones": perseveraciones,
                "intrusiones": intrusiones,
                "observaciones": observaciones,
            }

            _save_test_session(patient_id, "Fluidez-FAS", raw_data, scores)

            alert("Test de Fluidez Verbal guardado exitosamente!", alert_type="success")
            _display_scores(scores)


def _render_rey_copia_form(patient_id: str):
    """Render Rey Figure Copy test form"""
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
            [
                "Tipo I - Constructivo",
                "Tipo II - Detalles importantes",
                "Tipo III - Contorno general",
                "Tipo IV - Yuxtaposición",
                "Tipo V - Detalles sin estructura",
                "Tipo VI - Sustitución",
                "Tipo VII - Garabateo",
            ],
        )

        observaciones = st.text_area(
            "Observaciones",
            placeholder="Estrategia de copia, precisión, organización espacial...",
        )

        submitted = st.form_submit_button("💾 Calcular y Guardar")

        if submitted:
            patient = _get_patient_data(patient_id)
            scores = calculator.calculate(
                test_type="Rey-Copia",
                raw_score=puntuacion,
                age=patient["age"],
                education_years=patient["education_years"],
            )

            raw_data = {
                "puntuacion_bruta": puntuacion,
                "tiempo_segundos": tiempo,
                "tipo_copia": tipo_copia,
                "observaciones": observaciones,
            }

            _save_test_session(patient_id, "Rey-Copia", raw_data, scores)

            alert("Test Figura de Rey (Copia) guardado exitosamente!", alert_type="success")
            _display_scores(scores)


def _render_rey_memoria_form(patient_id: str):
    """Render Rey Figure Memory test form"""
    with st.form("rey_memoria_form"):
        st.subheader("🎨 Figura Compleja de Rey - Memoria")
        st.caption("Memoria visual diferida (típicamente después de 3-30 minutos)")

        col1, col2 = st.columns(2)
        with col1:
            puntuacion = st.number_input("Puntuación (0-36)", 0.0, 36.0, 18.0, 0.5)
        with col2:
            tiempo_demora = st.number_input("Tiempo de Demora (minutos)", 3, 60, 20, 1)

        observaciones = st.text_area(
            "Observaciones",
            placeholder="Elementos recordados, distorsiones, estrategias de recuperación...",
        )

        submitted = st.form_submit_button("💾 Calcular y Guardar")

        if submitted:
            patient = _get_patient_data(patient_id)
            scores = calculator.calculate(
                test_type="Rey-Memoria",
                raw_score=puntuacion,
                age=patient["age"],
                education_years=patient["education_years"],
            )

            raw_data = {
                "puntuacion_bruta": puntuacion,
                "tiempo_demora_minutos": tiempo_demora,
                "observaciones": observaciones,
            }

            _save_test_session(patient_id, "Rey-Memoria", raw_data, scores)

            alert("Test Figura de Rey (Memoria) guardado exitosamente!", alert_type="success")
            _display_scores(scores)


def _render_toulouse_pieron_form(patient_id: str):
    """Render Toulouse-Pieron attention test form with OCR"""
    st.subheader("👁️ Test de Atención Toulouse-Pieron")
    st.caption("Evaluación de atención sostenida y velocidad perceptiva")
    
    st.markdown("""
    **Instrucciones:**
    1. Sube una imagen del test completado (escaneado o fotografía)
    2. Configura la cuadrícula (filas × columnas) y sensibilidad OCR
    3. Usa OCR para detectar marcaciones automáticamente
    4. Revisa y ajusta los resultados según sea necesario
    
    **Tip**: Para marcas de lápiz claro, usa sensibilidad "Alta" o "Muy alta"
    """)
    
    # Image upload (outside form for OCR button)
    st.markdown("### 📸 Imagen del Test")
    uploaded_file = st.file_uploader(
        "Subir imagen del test",
        type=["png", "jpg", "jpeg"],
        help="Sube una fotografía o escaneo del test Toulouse-Pieron completado",
        key="toulouse_upload"
    )
    
    # Initialize session state for OCR results
    if 'ocr_results' not in st.session_state:
        st.session_state.ocr_results = None
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Test Toulouse-Pieron", width='stretch')
        
        # Save temp image for OCR
        temp_path = os.path.join('data', 'test_images', 'temp_ocr.png')
        image.save(temp_path, "PNG")
        
        # OCR Section
        st.markdown("---")
        st.markdown("### 🤖 Análisis Automático (OCR)")
        
        col_ocr1, col_ocr2, col_ocr3 = st.columns([2, 1, 1])
        with col_ocr1:
            grid_rows = st.number_input("Filas del test", min_value=10, max_value=50, value=40, 
                                       help="Número de filas en la cuadrícula del test (típicamente 40)")
            grid_cols = st.number_input("Columnas del test", min_value=20, max_value=60, value=40,
                                       help="Número de columnas en la cuadrícula del test (típicamente 40)")
        
        with col_ocr2:
            sensitivity = st.select_slider(
                "Sensibilidad OCR",
                options=["Muy baja", "Baja", "Media", "Alta", "Muy alta"],
                value="Alta",
                help="Ajusta según el tipo de marcado:\n- Muy alta: Lápiz muy claro\n- Alta: Lápiz normal\n- Media: Bolígrafo\n- Baja/Muy baja: Marcador grueso"
            )
            
            # Map sensitivity to threshold
            sensitivity_map = {
                "Muy baja": 0.30,
                "Baja": 0.22,
                "Media": 0.18,
                "Alta": 0.12,
                "Muy alta": 0.08
            }
            threshold = sensitivity_map[sensitivity]
        
        with col_ocr3:
            st.markdown("&nbsp;")  # Spacing
            if st.button("🔍 Analizar Imagen", type="primary"):
                from services.ocr_processor import ToulousePieronOCR
                
                with st.spinner("Analizando imagen..."):
                    # Create OCR processor with custom threshold
                    ocr = ToulousePieronOCR()
                    ocr.min_mark_density = threshold
                    
                    result = ocr.analyze_image(
                        temp_path,
                        expected_rows=grid_rows,
                        expected_cols=grid_cols
                    )
                    st.session_state.ocr_results = result
        
        # Show OCR results if available
        if st.session_state.ocr_results and st.session_state.ocr_results.get('success'):
            ocr = st.session_state.ocr_results
            
            st.markdown("---")
            st.markdown("### 📊 Resultados del Análisis")
            
            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.metric("Celdas Marcadas", ocr['marked_cells'])
            with col_res2:
                st.metric("Celdas No Marcadas", ocr['unmarked_cells'])
            with col_res3:
                st.metric("Confianza", f"{ocr['confidence']:.1%}")
            
            # Show images in expanders
            st.markdown("### 📸 Revisión de Imágenes")
            
            col_img1, col_img2 = st.columns(2)
            
            with col_img1:
                with st.expander("🔍 Imagen Convertida a Blanco y Negro", expanded=True):
                    if ocr.get('bw_image_path') and Path(ocr['bw_image_path']).exists():
                        st.image(ocr['bw_image_path'], width='stretch',
                                caption="Conversión B/N automática - Muestra cómo ve el OCR los marcados")
                    else:
                        alert("No disponible", alert_type="info")
            
            with col_img2:
                with st.expander("📍 Análisis de Cuadrícula", expanded=True):
                    if ocr.get('processed_image_path') and Path(ocr['processed_image_path']).exists():
                        st.image(ocr['processed_image_path'], width='stretch',
                                caption="Celdas detectadas como marcadas (verde) y no marcadas (rojo)")
                    else:
                        alert("No disponible", alert_type="info")
            alert(f"Análisis completado con {ocr['confidence']*100:.0f}% de confianza", alert_type="success")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Celdas Totales", ocr['total_cells_detected'])
            col2.metric("Celdas Marcadas", ocr['marked_cells'])
            col3.metric("Confianza", f"{ocr['confidence']*100:.0f}%")
            
            if ocr.get('processed_image_path') and os.path.exists(ocr['processed_image_path']):
                with st.expander("👁️ Ver Imagen Analizada"):
                    analyzed_image = Image.open(ocr['processed_image_path'])
                    st.image(analyzed_image, caption="Marcaciones detectadas (verde)", width='stretch')
        
        elif st.session_state.ocr_results and not st.session_state.ocr_results.get('success'):
            alert(f"OCR Error: {st.session_state.ocr_results.get('error')}", alert_type="warning")
            alert("Puedes introducir los valores manualmente a continuación.", alert_type="info")
    
    # Manual entry form
    with st.form("toulouse_pieron_form"):
        st.markdown("---")
        st.markdown("### 📊 Resultados del Test")
        
        # Pre-fill with OCR results if available
        default_total = st.session_state.ocr_results.get('total_cells_detected', 200) if st.session_state.ocr_results else 200
        default_marked = st.session_state.ocr_results.get('marked_cells', 150) if st.session_state.ocr_results else 150
        
        col1, col2 = st.columns(2)
        with col1:
            items_procesados = st.number_input(
                "Ítems Procesados (Total)",
                min_value=0,
                max_value=2000,
                value=default_total,
                step=1,
                help="Número total de ítems procesados. Se puede auto-rellenar con OCR."
            )
            aciertos = st.number_input(
                "Aciertos (Correctos)",
                min_value=0,
                max_value=items_procesados,
                value=min(default_marked, items_procesados),
                step=1,
                help="Número de marcaciones correctas. Ajusta el valor OCR si es necesario."
            )
        
        with col2:
            errores = st.number_input(
                "Errores (Omisiones + Falsos positivos)",
                min_value=0,
                max_value=items_procesados,
                value=10,
                step=1,
                help="Suma de omisiones y marcaciones incorrectas"
            )
            tiempo_minutos = st.number_input(
                "Tiempo (minutos)",
                min_value=1,
                max_value=60,
                value=10,
                step=1,
                help="Tiempo empleado en el test (típicamente 10 minutos)"
            )
        
        # Calculated metrics display
        productividad_neta = aciertos - errores
        tasa_aciertos = (aciertos / items_procesados * 100) if items_procesados > 0 else 0
        
        st.markdown("### 📈 Métricas Calculadas")
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Productividad Neta", f"{productividad_neta}")
        with metric_col2:
            st.metric("Tasa de Aciertos", f"{tasa_aciertos:.1f}%")
        
        # Observations
        observaciones = st.text_area(
            "Observaciones Clínicas (opcional)",
            placeholder="Estrategias, fatiga observada, patrón de errores, comportamiento...",
        )
        
        submitted = st.form_submit_button("💾 Calcular y Guardar")
        
        if submitted:
            if uploaded_file is None:
                alert("Por favor, sube una imagen del test antes de guardar.", alert_type="error")
                return
            
            # Save the uploaded image
            image_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_images')
            os.makedirs(image_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{patient_id[:8]}_Toulouse-Pieron_{timestamp}.png"
            image_path = os.path.join(image_dir, image_filename)
            
            # Save image
            image.save(image_path, "PNG")
            
            # Get patient data and calculate scores
            patient = _get_patient_data(patient_id)
            scores = calculator.calculate(
                test_type="Toulouse-Pieron",
                raw_score=productividad_neta,
                age=patient["age"],
                education_years=patient["education_years"],
            )
            
            # Prepare raw data
            raw_data = {
                "items_procesados": items_procesados,
                "aciertos": aciertos,
                "errores": errores,
                "tiempo_minutos": tiempo_minutos,
                "productividad_neta": productividad_neta,
                "tasa_aciertos": round(tasa_aciertos, 2),
                "image_path": image_path,
                "image_filename": image_filename,
                "observaciones": observaciones,
                "ocr_used": st.session_state.ocr_results is not None,
                "ocr_confidence": st.session_state.ocr_results.get('confidence', 0) if st.session_state.ocr_results else 0
            }
            
            _save_test_session(patient_id, "Toulouse-Pieron", raw_data, scores)
            
            alert("Test Toulouse-Pieron guardado exitosamente!", alert_type="success")
            alert(f"Imagen guardada: {image_filename}", alert_type="info")
            _display_scores(scores)
            
            # Clear OCR results for next test
            st.session_state.ocr_results = None


def _render_torre_de_londres_form(patient_id: str):
    """Render Tower of London test form with movement count and time per item"""
    from services.tower_of_london import calculator as tol_calculator
    
    db = SessionLocal()
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    db.close()
    
    st.markdown("### 🏰 Torre de Londres")
    
    # Initialize session state for item data if not exists
    if 'tol_items' not in st.session_state:
        st.session_state.tol_items = [
            {'movements': '', 'time_seconds': ''} for _ in range(10)
        ]
    
    # Create form with table-like input
    with st.form("torre_de_Londres_form"):
        st.markdown("#### Introduce movimientos y tiempo por ítem")
        
        # Apply CSS to constrain input field width aggressively
        st.write('''
        <style>
        /* Force narrow input boxes for Torre de Londres */
        div[data-testid="stForm"] input[type="text"] {
            width: 50px !important;
            padding: 4px 8px !important;
        }
        </style>
        ''', unsafe_allow_html=True)
        
        # Create columns for header with narrower proportions
        col1, col2, col3 = st.columns([0.5, 1, 1])
        with col1:
            st.markdown("**Ítem**")
        with col2:
            st.markdown("**Mov.**")
        with col3:
            st.markdown("**Seg.**")
        
        st.divider()
        
        # Create input rows for each item - free-form text inputs
        for i in range(10):
            item_num = i + 1
            col1, col2, col3 = st.columns([0.5, 1, 1])
            
            with col1:
                st.write(f"{item_num}")
            
            with col2:
                st.session_state.tol_items[i]['movements'] = st.text_input(
                    f"Movimientos {item_num}",
                    value=st.session_state.tol_items[i]['movements'],
                    placeholder="0",
                    max_chars=3,
                    key=f"tol_movements_{item_num}",
                    label_visibility="collapsed"
                )
            
            with col3:
                st.session_state.tol_items[i]['time_seconds'] = st.text_input(
                    f"Tiempo {item_num}",
                    value=st.session_state.tol_items[i]['time_seconds'],
                    placeholder="0",
                    max_chars=3,
                    key=f"tol_time_{item_num}",
                    label_visibility="collapsed"
                )
        
        st.divider()
        submitted = st.form_submit_button("💾 Calcular y Guardar", type="primary")
        
        if submitted:
            # Validate and convert inputs
            movement_counts = []
            time_seconds = []
            validation_errors = []
            
            for i in range(10):
                item_num = i + 1
                
                # Validate movements
                try:
                    mov = int(st.session_state.tol_items[i]['movements']) if st.session_state.tol_items[i]['movements'] else 0
                    if mov < 0:
                        validation_errors.append(f"Ítem {item_num}: Movimientos no puede ser negativo")
                    movement_counts.append(mov)
                except ValueError:
                    validation_errors.append(f"Ítem {item_num}: Movimientos debe ser un número")
                
                # Validate time
                try:
                    time_val = int(st.session_state.tol_items[i]['time_seconds']) if st.session_state.tol_items[i]['time_seconds'] else 0
                    if time_val < 0:
                        validation_errors.append(f"Ítem {item_num}: Tiempo no puede ser negativo")
                    time_seconds.append(time_val)
                except ValueError:
                    validation_errors.append(f"Ítem {item_num}: Tiempo debe ser un número")
            
            if validation_errors:
                alert("Errores en los datos:", alert_type="error")
                for error in validation_errors:
                    alert(f"• {error}", alert_type="error")
            else:
                # Calculate metrics (now includes time consideration)
                result = tol_calculator.calculate(movement_counts, time_seconds)
            
            if not result['valid']:
                alert("Errores en los datos:", alert_type="error")
                for error in result['errors']:
                    alert(f"• {error}", alert_type="error")
            else:
                # Prepare raw data for storage
                raw_data = {
                    'items': st.session_state.tol_items,
                    'movement_counts': movement_counts,
                    'item_results': result['item_results'],
                    'total_perfect_solutions': result['total_perfect_solutions'],
                    'total_movement_rating': result['total_movement_rating'],
                    'total_time_seconds': result['total_time_seconds'],
                    'execution_efficiency': result['execution_efficiency'],
                    'composite_raw_score': result['composite_raw_score']
                }
                
                # Calculate NEURONORMA scores using composite score (movements + time)
                scores = calculator.calculate(
                    test_type="Torre de Londres",
                    raw_score=result['composite_raw_score'],
                    age=patient.age,
                    education_years=patient.education_years
                )
                
                # Save test session
                _save_test_session(patient_id, "Torre de Londres", raw_data, scores)
                
                alert("Test Torre de Londres guardado exitosamente!", alert_type="success")
                _display_scores(scores)
                
                # Display detailed results
                st.markdown("---")
                st.markdown("#### 📊 Resultados Detallados")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Soluciones Perfectas", result['total_perfect_solutions'], 
                             help="Ítems resueltos con el mínimo de movimientos")
                with col2:
                    st.metric("Calificación Total", result['total_movement_rating'],
                             help="Suma de movimientos adicionales")
                with col3:
                    efficiency = (result['total_perfect_solutions'] / 10) * 100
                    st.metric("Eficiencia", f"{efficiency:.0f}%", 
                             help="% de ítems resueltos perfectamente")
                with col4:
                    st.metric("Tiempo Total", f"{result['total_time_seconds']}s",
                             help="Tiempo total invertido")
                
                # Display time efficiency
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    avg_time = result['total_time_seconds'] / 10
                    st.metric("Tiempo Promedio por Ítem", f"{avg_time:.1f}s",
                             help="Promedio de tiempo por ítem")
                with col2:
                    st.metric("Eficiencia de Ejecución", f"{result['execution_efficiency']:.2f}",
                             help="Factor de calidad temporal (0.90-1.00). Basado en velocidad de respuesta.")
                
                # Display item-by-item breakdown
                with st.expander("📋 Desglose Completo por Ítem"):
                    item_df = pd.DataFrame([
                        {
                            'Ítem': r['item'],
                            'Movimientos': r['movements_count'],
                            'Mínimo': r['minimum_movements'],
                            'Calificación': r['movement_rating'],
                            'Perfecto': '✅' if r['perfect'] else '❌',
                            'Tiempo (s)': r['time_seconds']
                        }
                        for r in result['item_results']
                    ])
                    st.dataframe(item_df, width='stretch', hide_index=True)


def _render_fluidez_semantic_form(patient_id: str):
    """Render Fluidez Semántica test form"""
    st.subheader("💬 Fluidez Verbal Semántica")
    st.caption("Test de fluidez semántica - Nombrar palabras de una categoría en 60 segundos")
    
    with st.form("form_fluidez_semantic"):
        st.markdown("**Categoría de Palabras (ej: Animales, Frutas, Profesiones)**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            categoria = st.text_input("Categoría", "Animales")
        with col2:
            palabras = st.number_input("Palabras válidas", min_value=0, max_value=100, value=20)
        with col3:
            errores = st.number_input("Errores/Perseveraciones", min_value=0, max_value=20, value=0)
        
        observaciones = st.text_area("Observaciones", "")
        submitted = st.form_submit_button("💾 Calcular y Guardar")
        
        if submitted:
            raw_data = {
                "categoria": categoria,
                "palabras": palabras,
                "errores": errores
            }
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "z_score": 0,
                "clasificacion": "Normal",
                "norma_aplicada": {
                    "fuente": "Simulado",
                    "test": "Fluidez-Semántica"
                }
            }
            _save_test_session(patient_id, "Fluidez-Semántica", raw_data, scores)
            alert("Test Fluidez Semántica guardado exitosamente!", alert_type="success")
            _display_scores(scores)


def _render_diva5_form(patient_id: str):
    """Render DIVA-5 test form"""
    st.subheader("📋 DIVA-5")
    st.caption("Entrevista Diagnóstica del TDAH en Adultos - Versión 5")
    
    with st.form("form_diva5"):
        st.markdown("**Síntomas de Infancia (Presente/Ausente)**")
        childhood_symptoms = {
            "Dificultad mantener atención": st.checkbox("Dificultad mantener atención", value=False),
            "Impulsividad": st.checkbox("Impulsividad", value=False),
            "Hiperactividad": st.checkbox("Hiperactividad", value=False),
            "Dificultades organizativas": st.checkbox("Dificultades organizativas", value=False),
        }
        
        st.markdown("**Síntomas Actuales**")
        current_symptoms = {
            "Atención": st.checkbox("Problemas de atención actuales", value=False),
            "Organización": st.checkbox("Dificultades con organización", value=False),
            "Impulsividad actual": st.checkbox("Impulsividad actual", value=False),
        }
        
        observaciones = st.text_area("Observaciones clínicas", "")
        submitted = st.form_submit_button("💾 Guardar DIVA-5")
        
        if submitted:
            raw_data = {"childhood": childhood_symptoms, "current": current_symptoms}
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "clasificacion": "Evaluación Completa",
                "norma_aplicada": {"fuente": "Simulado", "test": "DIVA-5"}
            }
            _save_test_session(patient_id, "DIVA-5", raw_data, scores)
            alert("DIVA-5 guardado exitosamente!", alert_type="success")


def _render_brief_a_form(patient_id: str):
    """Render BRIEF-A test form"""
    st.subheader("🧠 BRIEF-A")
    st.caption("Inventario de Evaluación de la Función Ejecutiva - Versión Adultos")
    
    with st.form("form_brief_a"):
        st.markdown("**Escala de Inhibición (Rango: 0-36)**")
        inhibicion = st.slider("Puntuación de Inhibición", 0, 36, 18)
        
        st.markdown("**Cambio Mental (Rango: 0-30)**")
        cambio = st.slider("Puntuación de Cambio Mental", 0, 30, 15)
        
        st.markdown("**Control Emocional (Rango: 0-24)**")
        emocional = st.slider("Control Emocional", 0, 24, 12)
        
        observaciones = st.text_area("Observaciones", "")
        submitted = st.form_submit_button("💾 Guardar BRIEF-A")
        
        if submitted:
            raw_data = {
                "inhibicion": inhibicion,
                "cambio_mental": cambio,
                "control_emocional": emocional
            }
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "clasificacion": "Normal",
                "norma_aplicada": {"fuente": "Simulado", "test": "BRIEF-A"}
            }
            _save_test_session(patient_id, "BRIEF-A", raw_data, scores)
            alert("BRIEF-A guardado exitosamente!", alert_type="success")


def _render_wais_iv_form(patient_id: str):
    """Render WAIS-IV test form"""
    st.subheader("🧩 WAIS-IV")
    st.caption("Subtests: Búsqueda de Símbolos y Clave de Números")
    
    with st.form("form_wais_iv"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Búsqueda de Símbolos**")
            simbolos_correctos = st.number_input("Correctos", 0, 100, 30)
            simbolos_errores = st.number_input("Errores", 0, 50, 2)
            simbolos_tiempo = st.number_input("Tiempo (segundos)", 0, 300, 120)
        
        with col2:
            st.markdown("**Clave de Números**")
            clave_correctos = st.number_input("Correctos (Clave)", 0, 150, 80)
            clave_errores = st.number_input("Errores (Clave)", 0, 50, 3)
            clave_tiempo = st.number_input("Tiempo (Clave)", 0, 300, 120)
        
        observaciones = st.text_area("Observaciones", "")
        submitted = st.form_submit_button("💾 Guardar WAIS-IV")
        
        if submitted:
            raw_data = {
                "busqueda_simbolos": {"correctos": simbolos_correctos, "errores": simbolos_errores, "tiempo": simbolos_tiempo},
                "clave_numeros": {"correctos": clave_correctos, "errores": clave_errores, "tiempo": clave_tiempo}
            }
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "clasificacion": "Normal",
                "norma_aplicada": {"fuente": "Simulado", "test": "WAIS-IV"}
            }
            _save_test_session(patient_id, "WAIS-IV", raw_data, scores)
            alert("WAIS-IV guardado exitosamente!", alert_type="success")


def _render_digitos_form(patient_id: str):
    """Render Dígitos test form"""
    st.subheader("🔢 Dígitos")
    st.caption("Test de Amplitud de Dígitos - Orden Directo, Inverso y Creciente")
    
    with st.form("form_digitos"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Orden Directo**")
            directo = st.number_input("Amplitud máxima", 1, 9, 5)
        
        with col2:
            st.markdown("**Orden Inverso**")
            inverso = st.number_input("Amplitud máxima (Inverso)", 1, 8, 4)
        
        with col3:
            st.markdown("**Orden Creciente**")
            creciente = st.number_input("Amplitud máxima (Creciente)", 1, 8, 4)
        
        observaciones = st.text_area("Observaciones", "")
        submitted = st.form_submit_button("💾 Guardar Dígitos")
        
        if submitted:
            raw_data = {
                "orden_directo": directo,
                "orden_inverso": inverso,
                "orden_creciente": creciente
            }
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "clasificacion": "Normal",
                "norma_aplicada": {"fuente": "Simulado", "test": "Dígitos"}
            }
            _save_test_session(patient_id, "Dígitos", raw_data, scores)
            alert("Test Dígitos guardado exitosamente!", alert_type="success")


def _render_d2r_form(patient_id: str):
    """Render Test d2-R form"""
    st.subheader("👁️ Test d2-R")
    st.caption("Test de Atención y Concentración")
    
    with st.form("form_d2r"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            correctos = st.number_input("Procesados correctamente", 0, 600, 250)
        
        with col2:
            omisiones = st.number_input("Omisiones", 0, 200, 10)
        
        with col3:
            comisiones = st.number_input("Comisiones", 0, 200, 5)
        
        concentracion = st.slider("Índice de concentración", 0.0, 1.0, 0.8, 0.01)
        observaciones = st.text_area("Observaciones", "")
        submitted = st.form_submit_button("💾 Guardar Test d2-R")
        
        if submitted:
            raw_data = {
                "correctos": correctos,
                "omisiones": omisiones,
                "comisiones": comisiones,
                "indice_concentracion": concentracion
            }
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "clasificacion": "Normal",
                "norma_aplicada": {"fuente": "Simulado", "test": "Test d2-R"}
            }
            _save_test_session(patient_id, "Test d2-R", raw_data, scores)
            alert("Test d2-R guardado exitosamente!", alert_type="success")


def _render_fdt_form(patient_id: str):
    """Render FDT (Five Digit Test) form"""
    st.subheader("5️⃣ FDT")
    st.caption("Test de los 5 Dígitos - Atención y Control Inhibitorio")
    
    with st.form("form_fdt"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Lectura (Reading)**")
            lectura_tiempo = st.number_input("Tiempo Lectura (s)", 0, 120, 45)
            lectura_errores = st.number_input("Errores Lectura", 0, 10, 0)
        
        with col2:
            st.markdown("**Conteo (Counting)**")
            conteo_tiempo = st.number_input("Tiempo Conteo (s)", 0, 120, 50)
            conteo_errores = st.number_input("Errores Conteo", 0, 10, 1)
        
        st.markdown("**Alternancia (Switching)**")
        alt_tiempo = st.number_input("Tiempo Alternancia (s)", 0, 120, 65)
        alt_errores = st.number_input("Errores Alternancia", 0, 10, 1)
        
        observaciones = st.text_area("Observaciones", "")
        submitted = st.form_submit_button("💾 Guardar FDT")
        
        if submitted:
            raw_data = {
                "lectura": {"tiempo": lectura_tiempo, "errores": lectura_errores},
                "conteo": {"tiempo": conteo_tiempo, "errores": conteo_errores},
                "alternancia": {"tiempo": alt_tiempo, "errores": alt_errores}
            }
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "clasificacion": "Normal",
                "norma_aplicada": {"fuente": "Simulado", "test": "FDT"}
            }
            _save_test_session(patient_id, "FDT", raw_data, scores)
            alert("FDT guardado exitosamente!", alert_type="success")


def _render_bads_zoo_form(patient_id: str):
    """Render BADS Zoo Map test form"""
    st.subheader("🗺️ BADS - Test del Mapa del Zoo")
    st.caption("Evaluación de Planificación y Organización (Batería BADS)")
    
    with st.form("form_bads_zoo"):
        col1, col2 = st.columns(2)
        
        with col1:
            errores_ruta = st.number_input("Errores de Ruta", 0, 20, 2)
            pasos_totales = st.number_input("Pasos Totales", 0, 50, 25)
        
        with col2:
            tiempo = st.number_input("Tiempo (segundos)", 0, 600, 180)
            eficiencia = st.slider("Eficiencia Planificación", 0.0, 1.0, 0.8, 0.1)
        
        observaciones = st.text_area("Observaciones", "")
        submitted = st.form_submit_button("💾 Guardar BADS Zoo")
        
        if submitted:
            raw_data = {
                "errores_ruta": errores_ruta,
                "pasos_totales": pasos_totales,
                "tiempo": tiempo,
                "eficiencia": eficiencia
            }
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "clasificacion": "Normal",
                "norma_aplicada": {"fuente": "Simulado", "test": "BADS-Zoo"}
            }
            _save_test_session(patient_id, "BADS-Zoo", raw_data, scores)
            alert("Test BADS Zoo guardado exitosamente!", alert_type="success")


def _render_bads_llave_form(patient_id: str):
    """Render BADS Key Search test form"""
    st.subheader("🔑 BADS - Búsqueda de la Llave")
    st.caption("Evaluación de Búsqueda Sistemática (Batería BADS)")
    
    with st.form("form_bads_llave"):
        col1, col2 = st.columns(2)
        
        with col1:
            errores_omision = st.number_input("Omisiones", 0, 30, 3)
            errores_duplicados = st.number_input("Duplicados", 0, 10, 1)
        
        with col2:
            area_cubierta = st.slider("Área Cubierta (%)", 0, 100, 85, 5)
            sistematica = st.slider("Sistematicidad", 0.0, 1.0, 0.8, 0.1)
        
        observaciones = st.text_area("Observaciones", "")
        submitted = st.form_submit_button("💾 Guardar BADS Llave")
        
        if submitted:
            raw_data = {
                "omisiones": errores_omision,
                "duplicados": errores_duplicados,
                "area_cubierta": area_cubierta,
                "sistematica": sistematica
            }
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "clasificacion": "Normal",
                "norma_aplicada": {"fuente": "Simulado", "test": "BADS-Llave"}
            }
            _save_test_session(patient_id, "BADS-Llave", raw_data, scores)
            alert("Test BADS Llave guardado exitosamente!", alert_type="success")


def _render_fcsrt_form(patient_id: str):
    """Render FCSRT test form"""
    st.subheader("📚 FCSRT")
    st.caption("Test de Memoria Libre y Facilitada Selectivamente (Buschke)")
    
    with st.form("form_fcsrt"):
        st.markdown("**Memoria Libre**")
        col1, col2 = st.columns(2)
        with col1:
            recuerdo_libre = st.number_input("Recuerdo Libre Inmediato", 0, 20, 10)
        with col2:
            recuerdo_facilitado = st.number_input("Recuerdo Facilitado", 0, 20, 12)
        
        st.markdown("**Memoria Diferida (tras intervalo)**")
        col1, col2 = st.columns(2)
        with col1:
            recuerdo_libre_dif = st.number_input("Recuerdo Libre Diferido", 0, 20, 8)
        with col2:
            recuerdo_facilitado_dif = st.number_input("Recuerdo Facilitado Diferido", 0, 20, 10)
        
        observaciones = st.text_area("Observaciones", "")
        submitted = st.form_submit_button("💾 Guardar FCSRT")
        
        if submitted:
            raw_data = {
                "recuerdo_libre": recuerdo_libre,
                "recuerdo_facilitado": recuerdo_facilitado,
                "recuerdo_libre_diferido": recuerdo_libre_dif,
                "recuerdo_facilitado_diferido": recuerdo_facilitado_dif
            }
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "clasificacion": "Normal",
                "norma_aplicada": {"fuente": "Simulado", "test": "FCSRT"}
            }
            _save_test_session(patient_id, "FCSRT", raw_data, scores)
            alert("FCSRT guardado exitosamente!", alert_type="success")


def _render_perfil_sensorial_form(patient_id: str):
    """Render Perfil Sensorial del Adulto form"""
    st.subheader("🎯 Perfil Sensorial del Adulto")
    st.caption("Cuestionario de Auto-evaluación Sensorial")
    
    with st.form("form_perfil_sensorial"):
        st.markdown("**Procesamiento Sensorial (Escala 1-5)**")
        
        col1, col2 = st.columns(2)
        with col1:
            sensibilidad_tactil = st.slider("Sensibilidad Táctil", 1, 5, 3)
            sensibilidad_auditiva = st.slider("Sensibilidad Auditiva", 1, 5, 3)
            sensibilidad_visual = st.slider("Sensibilidad Visual", 1, 5, 3)
        
        with col2:
            sensibilidad_olfativa = st.slider("Sensibilidad Olfativa", 1, 5, 3)
            sensibilidad_gustativa = st.slider("Sensibilidad Gustativa", 1, 5, 3)
            tolerancia_movimiento = st.slider("Tolerancia a Movimiento", 1, 5, 3)
        
        st.markdown("**Búsqueda Sensorial (Escala 1-5)**")
        busqueda = st.slider("Búsqueda de Estímulos", 1, 5, 3)
        
        observaciones = st.text_area("Observaciones", "")
        submitted = st.form_submit_button("💾 Guardar Perfil Sensorial")
        
        if submitted:
            raw_data = {
                "sensibilidad_tactil": sensibilidad_tactil,
                "sensibilidad_auditiva": sensibilidad_auditiva,
                "sensibilidad_visual": sensibilidad_visual,
                "sensibilidad_olfativa": sensibilidad_olfativa,
                "sensibilidad_gustativa": sensibilidad_gustativa,
                "tolerancia_movimiento": tolerancia_movimiento,
                "busqueda_sensorial": busqueda
            }
            scores = {
                "puntuacion_escalar": 10,
                "percentil": 50,
                "clasificacion": "Normal",
                "norma_aplicada": {"fuente": "Simulado", "test": "Perfil Sensorial"}
            }
            _save_test_session(patient_id, "Perfil Sensorial", raw_data, scores)
            alert("Perfil Sensorial guardado exitosamente!", alert_type="success")
