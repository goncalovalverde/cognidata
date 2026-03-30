"""
Dashboard page - Analytics and cognitive profile visualization
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os

from database.connection import SessionLocal
from models import Patient, TestSession, Protocol
from services.pdf_generator import pdf_generator
from services.audit import audit_service
from services.patient_protocol_service import patient_protocol_service
from components.design_components import alert, header


def render():
    """Render the dashboard page"""
    header("<i class='ph ph-chart-bar'></i> Panel de Análisis y Perfil Cognitivo", "")

    # Create tabs
    tab1, tab2 = st.tabs(["🧪 Perfil Cognitivo", "📑 Estadísticas de Protocolos"])
    
    with tab1:
        _render_cognitive_profile()
    
    with tab2:
        _render_protocol_statistics()


def _render_cognitive_profile():
    """Render cognitive profile for a patient"""
    db = SessionLocal()
    try:
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()

        if not patients:
            st.warning(
                "⚠️ No hay pacientes registrados. Crea uno primero en la sección 'Pacientes'."
            )
            return

        patient_options = {
            f"{p.id[:8]}... ({p.age} años, {p.education_years} años escolaridad)": p.id
            for p in patients
        }
        selected_patient_label = st.selectbox(
            "Seleccionar Paciente para Análisis", list(patient_options.keys()), key="profile_patient"
        )
        selected_patient_id = patient_options[selected_patient_label]

        sessions = (
            db.query(TestSession)
            .filter_by(patient_id=selected_patient_id)
            .order_by(TestSession.date.desc())
            .all()
        )
        patient = db.query(Patient).filter_by(id=selected_patient_id).first()

        patient_data = {
            "id": patient.id,
            "age": patient.age,
            "education_years": patient.education_years,
            "laterality": patient.laterality,
        }

        sessions_data = []
        for session in sessions:
            sessions_data.append(
                {
                    "test_type": session.test_type,
                    "date": session.date,
                    "raw_data": session.get_raw_data(),
                    "calculated_scores": session.get_calculated_scores(),
                    "qualitative_data": session.get_qualitative_data(),
                }
            )
    finally:
        db.close()

    if not sessions_data:
        st.info(
            f"👤 Paciente seleccionado: {patient_data['age']} años, {patient_data['education_years']} años de escolaridad"
        )
        st.warning(
            "Este paciente no tiene tests realizados aún. Ve a la sección 'Tests' para realizar evaluaciones."
        )
    else:
        _render_patient_info(patient_data, len(sessions_data))
        _prepare_chart_data(sessions_data)
        _render_radar_chart()
        _render_percentile_chart()
        _render_summary_table(sessions_data)
        _render_interpretation()
        _render_export_section(patient_data, sessions_data)


def _render_protocol_statistics():
    """Render protocol statistics and trending"""
    db = SessionLocal()
    try:
        protocols = db.query(Protocol).all()
        
        if not protocols:
            alert("No hay protocolos definidos. Crea uno en la sección 'Protocolos'", type="info")
            return
        
        # Protocol usage statistics
        st.subheader("📊 Uso de Protocolos")
        
        col1, col2, col3 = st.columns(3)
        
        # Count protocols
        col1.metric("Total de Protocolos", len(protocols))
        
        # Count assignments
        db_assign = SessionLocal()
        try:
            from models import PatientProtocol
            assignments = db_assign.query(PatientProtocol).all()
            col2.metric("Protocolos Asignados", len(assignments))
            
            # Count completed
            completed = len([a for a in assignments if a.status == "completed"])
            col3.metric("Protocolos Completados", completed)
        finally:
            db_assign.close()
        
        st.markdown("---")
        
        # Protocol details
        st.subheader("Detalles por Protocolo")
        
        for protocol in protocols:
            assignments = patient_protocol_service.get_patient_protocols_for_protocol(protocol.id)
            
            completed_count = sum(1 for a in assignments if a.status == "completed")
            in_progress_count = sum(1 for a in assignments if a.status == "in_progress")
            pending_count = sum(1 for a in assignments if a.status == "pending")
            
            with st.expander(f"🧪 {protocol.name} ({len(assignments)} pacientes)"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total", len(assignments))
                col2.metric("Completados", completed_count)
                col3.metric("En Progreso", in_progress_count)
                col4.metric("Pendientes", pending_count)
                
                # Progress bar
                if len(assignments) > 0:
                    percentage = int((completed_count / len(assignments)) * 100)
                    st.progress(percentage / 100)
                    st.caption(f"Tasa de Completación: {percentage}%")
                
                st.markdown(f"**Categoría:** {protocol.category or '—'}")
                st.markdown(f"**Testes:** {len(protocol.tests)}")
        
        st.markdown("---")
        
        # Chart: Completion rate by protocol
        st.subheader("📈 Gráfico de Completación")
        
        protocol_names = []
        completion_rates = []
        
        for protocol in protocols:
            assignments = patient_protocol_service.get_patient_protocols_for_protocol(protocol.id)
            if len(assignments) > 0:
                completed = sum(1 for a in assignments if a.status == "completed")
                rate = int((completed / len(assignments)) * 100)
                protocol_names.append(protocol.name[:20])
                completion_rates.append(rate)
        
        if protocol_names:
            fig = go.Figure(data=go.Bar(
                x=protocol_names,
                y=completion_rates,
                marker_color=['#22c55e' if r >= 75 else '#3b82f6' if r >= 50 else '#fbbf24' for r in completion_rates],
                text=completion_rates,
                textposition='auto',
            ))
            fig.update_layout(
                title="Tasa de Completación por Protocolo",
                xaxis_title="Protocolo",
                yaxis_title="Porcentaje Completado (%)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    finally:
        db.close()


def _render_patient_info(patient_data: dict, session_count: int):
    """Render patient information header"""
    col1, col2, col3 = st.columns(3)
    col1.metric("👤 Edad", f"{patient_data['age']} años")
    col2.metric("🎓 Escolaridad", f"{patient_data['education_years']} años")
    col3.metric("🧪 Tests Realizados", session_count)
    st.markdown("---")


def _prepare_chart_data(sessions: list):
    """Prepare data for charts - stored in session state"""
    test_names = []
    pe_scores = []
    percentiles = []
    clasificaciones = []

    for session in sessions:
        scores = session.get("calculated_scores", {})
        if scores:
            test_names.append(session.get("test_type", ""))
            pe_scores.append(scores.get("puntuacion_escalar", 10))
            percentiles.append(scores.get("percentil", 50))
            clasificaciones.append(scores.get("clasificacion", "N/A"))

    st.session_state["chart_data"] = {
        "test_names": test_names,
        "pe_scores": pe_scores,
        "percentiles": percentiles,
        "clasificaciones": clasificaciones,
        "sessions": sessions,
    }


def _render_radar_chart():
    """Render radar chart for cognitive profile"""
    data = st.session_state.get("chart_data", {})
    test_names = data.get("test_names", [])
    pe_scores = data.get("pe_scores", [])

    if not test_names:
        return

    st.subheader("🎯 Perfil Cognitivo - Puntuaciones Escalares")

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=pe_scores,
            theta=test_names,
            fill="toself",
            name="Perfil del Paciente",
            line=dict(color="#2563eb", width=2),
            marker=dict(size=8, color="#2563eb"),
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            r=[10] * len(test_names),
            theta=test_names,
            fill=None,
            name="Media Poblacional (pe=10)",
            line=dict(color="#10b981", width=2, dash="dash"),
            marker=dict(size=0),
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 19],
                tickmode="linear",
                tick0=0,
                dtick=5,
                showline=True,
                gridcolor="#e5e7eb",
            ),
            angularaxis=dict(gridcolor="#e5e7eb"),
        ),
        showlegend=True,
        height=500,
        title=dict(
            text="Puntuaciones Escalares (pe) - Escala: 1-19, Media: 10, DE: 3",
            x=0.5,
            xanchor="center",
        ),
    )
    st.plotly_chart(fig, width='stretch')
    st.markdown("---")


def _render_percentile_chart():
    """Render percentile bar chart"""
    data = st.session_state.get("chart_data", {})
    test_names = data.get("test_names", [])
    percentiles = data.get("percentiles", [])
    clasificaciones = data.get("clasificaciones", [])

    if not test_names:
        return

    st.subheader("📊 Percentiles por Test")

    fig_bar = go.Figure()

    colors = []
    for clasificacion in clasificaciones:
        if clasificacion == "Superior":
            colors.append("#10b981")
        elif clasificacion == "Normal":
            colors.append("#3b82f6")
        elif clasificacion == "Limítrofe":
            colors.append("#f59e0b")
        else:
            colors.append("#ef4444")

    fig_bar.add_trace(
        go.Bar(
            x=test_names,
            y=percentiles,
            text=[f"{p}%" for p in percentiles],
            textposition="outside",
            marker=dict(color=colors),
            name="Percentil",
        )
    )

    fig_bar.add_hline(
        y=75,
        line_dash="dash",
        line_color="#10b981",
        annotation_text="Superior (P75)",
        annotation_position="right",
    )
    fig_bar.add_hline(
        y=25,
        line_dash="dash",
        line_color="#3b82f6",
        annotation_text="Normal (P25)",
        annotation_position="right",
    )
    fig_bar.add_hline(
        y=10,
        line_dash="dash",
        line_color="#f59e0b",
        annotation_text="Limítrofe (P10)",
        annotation_position="right",
    )

    fig_bar.update_layout(
        yaxis=dict(title="Percentil", range=[0, 100]),
        xaxis=dict(title="Test"),
        height=400,
        showlegend=False,
        title="Distribución de Percentiles",
    )
    st.plotly_chart(fig_bar, width='stretch')
    st.markdown("---")


def _render_summary_table(sessions: list):
    """Render summary results table"""
    data = st.session_state.get("chart_data", {})
    test_names = data.get("test_names", [])
    pe_scores = data.get("pe_scores", [])
    percentiles = data.get("percentiles", [])
    clasificaciones = data.get("clasificaciones", [])

    if not test_names:
        return

    st.subheader("📋 Resumen de Resultados")

    df_results = pd.DataFrame(
        {
            "Test": test_names,
            "Fecha": [s.get("date").strftime("%d/%m/%Y %H:%M") for s in sessions],
            "pe": pe_scores,
            "Percentil": [f"{p}%" for p in percentiles],
            "Clasificación": clasificaciones,
        }
    )

    st.dataframe(df_results, width='stretch', hide_index=True)


def _render_interpretation():
    """Render interpretation section"""
    data = st.session_state.get("chart_data", {})
    pe_scores = data.get("pe_scores", [])
    percentiles = data.get("percentiles", [])
    test_names = data.get("test_names", [])

    if not pe_scores:
        return

    st.markdown("---")
    st.subheader("💡 Interpretación")

    mean_pe = sum(pe_scores) / len(pe_scores)
    mean_percentil = sum(percentiles) / len(percentiles)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Media de Puntuación Escalar", f"{mean_pe:.1f}")
        if mean_pe >= 13:
            alert("Rendimiento global superior a la media", type="success")
        elif mean_pe >= 7:
            alert("Rendimiento global dentro de la normalidad", type="info")
        elif mean_pe >= 4:
            alert("Rendimiento global en rango limítrofe", type="warning")
        else:
            alert("Rendimiento global por debajo de lo esperado", type="error")

    with col2:
        st.metric("Media de Percentil", f"{mean_percentil:.1f}%")
        st.caption("Comparación con población normativa según edad y escolaridad")

    if len(pe_scores) > 1:
        max_idx = pe_scores.index(max(pe_scores))
        min_idx = pe_scores.index(min(pe_scores))

        col1, col2 = st.columns(2)
        with col1:
            st.success(
                f"**💪 Punto Fuerte:** {test_names[max_idx]} (pe={pe_scores[max_idx]})"
            )
        with col2:
            st.warning(
                f"**⚠️ Área de Dificultad:** {test_names[min_idx]} (pe={pe_scores[min_idx]})"
            )


def _render_export_section(patient_data: dict, sessions_data: list):
    """Render PDF export section"""
    st.markdown("---")
    st.subheader("📄 Exportar Informe")

    if st.button("📥 Generar Informe PDF", type="primary"):
        with st.spinner("Generando informe PDF..."):
            try:
                pdf_path = pdf_generator.generate_report(
                    patient_data=patient_data, test_sessions=sessions_data
                )

                audit_service.log_report_generate(
                    patient_data["id"], len(sessions_data)
                )

                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()

                alert("Informe generado exitosamente", type="success")
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_bytes,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                )

            except Exception as e:
                alert(f"Error al generar PDF: {str(e)}", type="error")
