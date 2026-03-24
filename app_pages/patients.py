"""
Patients page - Patient CRUD operations
"""

import streamlit as st
from database.connection import SessionLocal
from models import Patient
from services.audit import audit_service


def render():
    """Render the patients page"""
    tab1, tab2 = st.tabs(["📋 Lista de Pacientes", "➕ Nuevo Paciente"])

    with tab1:
        _render_patient_list()

    with tab2:
        _render_new_patient_form()


def _render_patient_list():
    """Render the patient list with delete functionality"""
    st.subheader("Lista de Pacientes")

    db = SessionLocal()
    try:
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()

        if patients:
            for patient in patients:
                patient_id = patient.id
                age = patient.age
                education = patient.education_years
                laterality = patient.laterality
                created_at = patient.created_at

                with st.expander(
                    f"ID: {patient_id[:8]}... | {age} años | {laterality}"
                ):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Edad", f"{age} años")
                    col2.metric("Escolaridad", f"{education} años")
                    col3.metric("Lateralidad", laterality.capitalize())

                    st.caption(f"Creado: {created_at.strftime('%d/%m/%Y %H:%M')}")

                    _render_delete_button(patient_id)
        else:
            st.info(
                "No hay pacientes registrados. Crea uno en la pestaña 'Nuevo Paciente'"
            )
    finally:
        db.close()


def _render_delete_button(patient_id: str):
    """Render delete button with confirmation"""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.warning(f"¿Eliminar paciente {patient_id[:8]}...?")

    with col2:
        if st.button("Sí, eliminar", key=f"del_{patient_id}", type="primary"):
            db = SessionLocal()
            try:
                patient_to_delete = db.query(Patient).filter_by(id=patient_id).first()
                if patient_to_delete:
                    db.delete(patient_to_delete)
                    db.commit()
            finally:
                db.close()

            audit_service.log_patient_delete(patient_id)
            st.success("Paciente eliminado")
            st.rerun()


def _render_new_patient_form():
    """Render the new patient form"""
    st.subheader("Registrar Nuevo Paciente")

    with st.form("new_patient_form"):
        age = st.number_input("Edad", min_value=18, max_value=100, value=65)
        education_years = st.number_input(
            "Años de Escolaridad", min_value=0, max_value=25, value=12
        )
        laterality = st.selectbox("Lateralidad", ["diestro", "zurdo", "ambidextro"])

        submitted = st.form_submit_button("Guardar Paciente")

        if submitted:
            db = SessionLocal()
            try:
                new_patient = Patient(
                    age=age, education_years=education_years, laterality=laterality
                )
                db.add(new_patient)
                db.commit()
                patient_id = str(new_patient.id)
            finally:
                db.close()

            audit_service.log_patient_create(
                patient_id,
                {
                    "age": age,
                    "education_years": education_years,
                    "laterality": laterality,
                },
            )

            st.success(f"✅ Paciente creado con ID: {patient_id[:12]}...")
            st.balloons()
