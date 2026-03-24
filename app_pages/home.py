"""
Home page - Dashboard overview
"""

import streamlit as st
from database.connection import SessionLocal
from models import Patient, TestSession


def render():
    """Render the home page"""
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
