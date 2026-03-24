"""
Tests page - Neuropsychological test administration
"""

import streamlit as st
from database.connection import SessionLocal
from models import Patient, TestSession
from services.normatives import calculator
from services.audit import audit_service


def render():
    """Render the tests page"""
    st.subheader("Realizar Test Neuropsicológico")

    db = SessionLocal()
    try:
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()

        if not patients:
            st.warning(
                "⚠️ No hay pacientes registrados. Crea uno primero en la sección 'Pacientes'."
            )
        else:
            patient_options = {f"{p.id[:8]}... ({p.age} años)": p.id for p in patients}
            selected_patient_label = st.selectbox(
                "Seleccionar Paciente", list(patient_options.keys())
            )
            selected_patient_id = patient_options[selected_patient_label]

            test_type = st.selectbox(
                "Tipo de Test",
                ["TMT-A", "TMT-B", "TAVEC", "Fluidez-FAS", "Rey-Copia", "Rey-Memoria"],
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
            elif test_type == "Rey-Copia":
                _render_rey_copia_form(selected_patient_id)
            elif test_type == "Rey-Memoria":
                _render_rey_memoria_form(selected_patient_id)
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

            st.success("✅ Test TMT-A guardado exitosamente!")
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

            st.success("✅ Test TMT-B guardado exitosamente!")
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
        st.info(f"**Total Lista A (ensayos 1-5):** {total_a} palabras")

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

            st.success("✅ Test TAVEC guardado exitosamente!")
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
        st.info(f"**Total F-A-S:** {total_fas} palabras")

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

            st.success("✅ Test de Fluidez Verbal guardado exitosamente!")
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

            st.success("✅ Test Figura de Rey (Copia) guardado exitosamente!")
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

            st.success("✅ Test Figura de Rey (Memoria) guardado exitosamente!")
            _display_scores(scores)
