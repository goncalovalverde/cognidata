"""
Patients page - Patient CRUD operations
"""

import streamlit as st
from database.connection import SessionLocal
from models import Patient
from services.audit import audit_service
from services.patient_protocol_service import patient_protocol_service
from services.protocol_service import protocol_service
from utils.alerts import modal_error
from components.design_components import alert, header


def render():
    """Render the patients page"""
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Pacientes", "➕ Nuevo Paciente", "📑 Protocolos"])

    with tab1:
        _render_patient_list()

    with tab2:
        _render_new_patient_form()
    
    with tab3:
        _render_patient_protocols()


def _render_patient_list():
    """Render the patient list with delete functionality"""
    st.subheader("Lista de Pacientes")

    db = SessionLocal()
    try:
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()

        if patients:
            for i, patient in enumerate(patients):
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

                    # Delete button triggers modal via session state
                    if st.button("🗑️ Eliminar", key=f"delete_patient_{patient_id}", use_container_width=True, type="secondary"):
                        st.session_state.show_delete_patient_modal = True
                        st.session_state.delete_patient_id = patient_id
                        st.rerun()
                    
                    # Check if delete modal should be shown
                    if st.session_state.get("show_delete_patient_modal", False) and st.session_state.get("delete_patient_id") == patient_id:
                        show_delete_patient_modal(patient_id)
        else:
            alert(
                "No hay pacientes registrados. Crea uno en la pestaña 'Nuevo Paciente'", 
                alert_type="info"
            )
    finally:
        db.close()


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

            alert(f"Paciente creado con ID: {patient_id[:12]}...", alert_type="success")
            st.balloons()


def _render_patient_protocols():
    """Render protocol assignment management for patients"""
    st.subheader("Gestión de Protocolos por Paciente")
    
    db = SessionLocal()
    try:
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
        
        if not patients:
            alert("No hay pacientes registrados", alert_type="info")
            return
        
        # Select patient
        patient_options = {p.id: f"ID: {p.id[:8]}... ({p.age} años)" for p in patients}
        selected_patient_id = st.selectbox(
            "Selecciona un paciente",
            list(patient_options.keys()),
            format_func=lambda x: patient_options[x],
            key="protocol_patient_select"
        )
        
        if not selected_patient_id:
            return
        
        selected_patient = next(p for p in patients if p.id == selected_patient_id)
        
        # Display patient info
        col1, col2, col3 = st.columns(3)
        col1.metric("Edad", f"{selected_patient.age} años")
        col2.metric("Escolaridad", f"{selected_patient.education_years} años")
        col3.metric("Lateralidad", selected_patient.laterality.capitalize())
        
        st.markdown("---")
        
        # Get assigned protocols
        assignments = patient_protocol_service.get_patient_protocols(selected_patient_id)
        
        if assignments:
            st.subheader("📑 Protocolos Asignados")
            
            for assignment in assignments:
                protocol = assignment.protocol
                status = assignment.status
                
                # Get completion status
                completion = patient_protocol_service.get_protocol_completion_status(
                    selected_patient_id, protocol.id
                )
                
                # Display protocol card
                with st.expander(
                    f"🧪 **{protocol.name}** - {status.upper()} ({completion['percentage']}%)",
                    expanded=False
                ):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Descripción:** {protocol.description or '—'}")
                        st.markdown(f"**Categoría:** {protocol.category or '—'}")
                        st.markdown(f"**Testes:** {len(protocol.tests)}")
                        st.markdown(f"**Completados:** {completion['completed_tests']}/{completion['total_tests']}")
                        
                        # Progress bar
                        st.progress(completion['percentage'] / 100)
                    
                    with col2:
                        if st.button("🗑️ Desasignar", key=f"unassign_{protocol.id}", use_container_width=True):
                            st.session_state.show_unassign_confirmation = True
                            st.session_state.unassign_protocol_id = protocol.id
                            st.rerun()
                
                # Check if unassignment modal should be shown
                if st.session_state.get("show_unassign_confirmation", False) and st.session_state.get("unassign_protocol_id") == protocol.id:
                    show_unassign_protocol_modal(selected_patient_id, protocol.id, protocol.name)
        
        st.markdown("---")
        
        # Get available protocols
        available = patient_protocol_service.get_available_protocols(selected_patient_id)
        
        if available:
            st.subheader("➕ Asignar Nuevo Protocolo")
            
            protocol_options = {p.id: p.name for p in available}
            selected_protocol_id = st.selectbox(
                "Elige un protocolo",
                list(protocol_options.keys()),
                format_func=lambda x: protocol_options[x],
                key="available_protocols"
            )
            
            if st.button("✅ Asignar Protocolo", use_container_width=True, type="primary"):
                patient_protocol_service.assign_protocol(selected_patient_id, selected_protocol_id)
                alert("Protocolo asignado correctamente", alert_type="success")
                st.rerun()
        else:
            if assignments:
                alert("Todos los protocolos disponibles ya están asignados a este paciente", alert_type="info")
            else:
                alert("No hay protocolos disponibles. Crea uno en la pestaña 'Protocolos'", alert_type="warning")
    
    finally:
        db.close()


@st.dialog("⚠️ Confirmar Desasignación", width="large")
def show_unassign_protocol_modal(patient_id: str, protocol_id: str, protocol_name: str):
    """Show modal to confirm protocol unassignment"""
    st.markdown(f"""
    <div style='
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 16px;
        border-radius: 6px;
        color: #212121;
        font-size: 16px;
    '>
        ¿Desea desasignar el protocolo "<b>{protocol_name}</b>"?
        <br><br>
        Los testes ya realizados permanecerán en el historial del paciente.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Sí, desasignar", type="primary", use_container_width=True):
            patient_protocol_service.unassign_protocol(patient_id, protocol_id)
            st.toast(f"✅ Protocolo '{protocol_name}' desasignado correctamente", icon="✅")
            st.session_state.show_unassign_confirmation = False
            st.rerun()
    
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.show_unassign_confirmation = False
            st.rerun()


@st.dialog("⚠️ Confirmar Eliminación de Paciente", width="large")
def show_delete_patient_modal(patient_id: str):
    """Show modal to confirm patient deletion"""
    st.markdown(f"""
    <div style='
        background-color: #ffebee;
        border-left: 4px solid #ef5350;
        padding: 16px;
        border-radius: 6px;
        color: #212121;
        font-size: 16px;
    '>
        ¿Está seguro de que desea eliminar el paciente?
        <br><br>
        <b>ID: {patient_id[:12]}...</b>
        <br><br>
        Esta acción es <b>irreversible</b> y eliminará todos los tests asociados.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Sí, eliminar", type="primary", use_container_width=True):
            db = SessionLocal()
            try:
                patient_to_delete = db.query(Patient).filter_by(id=patient_id).first()
                if patient_to_delete:
                    db.delete(patient_to_delete)
                    db.commit()
            finally:
                db.close()
            
            audit_service.log_patient_delete(patient_id)
            st.toast(f"✅ Paciente eliminado correctamente", icon="✅")
            
            st.session_state.show_delete_patient_modal = False
            st.session_state.delete_patient_id = None
            st.rerun()
    
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.show_delete_patient_modal = False
            st.rerun()

