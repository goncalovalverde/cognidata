"""
Configuration page - Settings, backup, and audit logs
"""

import streamlit as st
import shutil
from datetime import datetime
import pandas as pd

from services.audit import audit_service


def render():
    """Render the configuration page"""
    col1, col2 = st.columns(2)

    with col1:
        _render_backup_section()

    with col2:
        _render_export_section()

    st.markdown("---")
    _render_audit_logs()


def _render_backup_section():
    """Render backup functionality"""
    st.markdown("### 💾 Backup de Datos")

    if st.button("Crear Backup Ahora"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"cognidata_{timestamp}.db"

        try:
            shutil.copy2("cognidata.db", f"backups/{backup_filename}")
            audit_service.log_backup_create(backup_filename)
            st.success(f"✅ Backup creado: {backup_filename}")
        except Exception as e:
            st.error(f"❌ Error al crear backup: {str(e)}")


def _render_export_section():
    """Render data export functionality"""
    st.markdown("### 📤 Exportar Datos")

    if st.button("Exportar JSON"):
        st.info("🚧 Funcionalidad en desarrollo")


def _render_audit_logs():
    """Render audit log viewer"""
    st.markdown("### 📋 Registro de Auditoría")

    with st.expander("Ver logs de auditoría"):
        log_filter = st.selectbox(
            "Filtrar por tipo:",
            [
                "Todos",
                "patient.create",
                "patient.delete",
                "test.create",
                "report.generate",
                "backup.create",
            ],
        )

        action_filter = None if log_filter == "Todos" else log_filter

        logs = audit_service.get_logs(action=action_filter, limit=50)

        if logs:
            log_data = []
            for log in logs:
                log_data.append(
                    {
                        "Fecha/Hora": log.timestamp.strftime("%d/%m/%Y %H:%M"),
                        "Acción": log.action,
                        "Recurso": log.resource_type,
                        "ID Recurso": log.resource_id or "N/A",
                        "IP": log.ip_address,
                    }
                )

            df_logs = pd.DataFrame(log_data)
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
        else:
            st.info("No hay registros de auditoría")
