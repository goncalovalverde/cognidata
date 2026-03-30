"""
Configuration page - Settings, backup, audit logs, and user management
"""

import streamlit as st
import shutil
from datetime import datetime
import pandas as pd

from services.audit import audit_service
from services.user_service import (
    create_user, update_user, delete_user, get_all_users, change_password, hash_password
)
from models import UserRole
from components.design_components import alert


def render():
    """Render the configuration page"""
    col1, col2 = st.columns(2)

    with col1:
        _render_backup_section()

    with col2:
        _render_export_section()

    st.markdown("---")
    _render_user_management()
    
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
            alert(f"Backup creado: {backup_filename}", type="success")
        except Exception as e:
            alert(f"Error al crear backup: {str(e)}", type="error")


def _render_export_section():
    """Render data export functionality"""
    st.markdown("### 📤 Exportar Datos")

    if st.button("Exportar JSON"):
        alert("Funcionalidad en desarrollo", type="info")


def _render_user_management():
    """Render user management section"""
    st.markdown("### 👥 Gestión de Usuarios")
    
    tab1, tab2, tab3 = st.tabs(["Ver Usuarios", "Crear Usuario", "Editar/Eliminar Usuario"])
    
    with tab1:
        _render_view_users()
    
    with tab2:
        _render_create_user()
    
    with tab3:
        _render_edit_delete_user()


def _render_view_users():
    """Render user list"""
    st.subheader("📋 Lista de Usuarios")
    
    try:
        users = get_all_users()
        
        if users:
            user_data = []
            for user in users:
                user_data.append({
                    "Usuario": user.username,
                    "Nombre Completo": user.full_name or "N/A",
                    "Rol": user.role.value,
                    "Activo": "✅ Sí" if user.is_active else "❌ No",
                    "Creado": user.created_at.strftime("%d/%m/%Y %H:%M"),
                })
            
            df_users = pd.DataFrame(user_data)
            st.dataframe(df_users, width='stretch', hide_index=True)
        else:
            alert("No hay usuarios registrados", type="info")
    except Exception as e:
        alert(f"Error al cargar usuarios: {str(e)}", type="error")


def _render_create_user():
    """Render create user form"""
    st.subheader("➕ Crear Nuevo Usuario")
    
    with st.form("create_user_form"):
        username = st.text_input("Nombre de Usuario", placeholder="ejemplo_usuario")
        password = st.text_input("Contraseña", type="password", placeholder="Ingrese contraseña")
        password_confirm = st.text_input("Confirmar Contraseña", type="password", placeholder="Repita contraseña")
        full_name = st.text_input("Nombre Completo", placeholder="Juan Pérez")
        role = st.selectbox(
            "Rol",
            [UserRole.ADMIN.value, UserRole.PRACTITIONER.value, UserRole.VIEWER.value],
            index=1  # Default to PRACTITIONER
        )
        
        submitted = st.form_submit_button("➕ Crear Usuario", type="primary")
        
        if submitted:
            # Validation
            errors = []
            
            if not username or len(username) < 3:
                errors.append("El nombre de usuario debe tener al menos 3 caracteres")
            
            if not password or len(password) < 6:
                errors.append("La contraseña debe tener al menos 6 caracteres")
            
            if password != password_confirm:
                errors.append("Las contraseñas no coinciden")
            
            if not full_name or len(full_name) < 3:
                errors.append("Ingrese un nombre completo válido")
            
            if errors:
                for error in errors:
                    alert(error, type="error")
            else:
                try:
                    role_enum = UserRole[role.upper()]
                    create_user(username, password, full_name, role_enum)
                    alert(f"Usuario '{username}' creado exitosamente", type="success")
                    st.rerun()
                except ValueError as e:
                    alert(f"Error: {str(e)}", type="error")
                except Exception as e:
                    alert(f"Error al crear usuario: {str(e)}", type="error")


def _render_edit_delete_user():
    """Render edit and delete user functionality"""
    st.subheader("✏️ Editar o Eliminar Usuario")
    
    try:
        users = get_all_users()
        
        if not users:
            alert("No hay usuarios para editar", type="info")
            return
        
        user_options = {u.username: u for u in users}
        selected_username = st.selectbox(
            "Seleccionar Usuario",
            list(user_options.keys()),
            key="user_select"
        )
        
        if selected_username:
            selected_user = user_options[selected_username]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Editar Información")
                with st.form("edit_user_form"):
                    new_full_name = st.text_input(
                        "Nombre Completo",
                        value=selected_user.full_name or "",
                        placeholder="Nombre completo"
                    )
                    new_role = st.selectbox(
                        "Rol",
                        [UserRole.ADMIN.value, UserRole.PRACTITIONER.value, UserRole.VIEWER.value],
                        index=[UserRole.ADMIN.value, UserRole.PRACTITIONER.value, UserRole.VIEWER.value].index(selected_user.role.value)
                    )
                    
                    edit_submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
                    
                    if edit_submitted:
                        try:
                            role_enum = UserRole[new_role.upper()]
                            update_user(selected_username, new_full_name, role_enum)
                            alert("Usuario actualizado exitosamente", type="success")
                            st.rerun()
                        except Exception as e:
                            alert(f"Error al actualizar: {str(e)}", type="error")
            
            with col2:
                st.markdown("#### Cambiar Contraseña")
                with st.form("change_password_form"):
                    new_password = st.text_input("Nueva Contraseña", type="password", placeholder="Nueva contraseña")
                    new_password_confirm = st.text_input("Confirmar Contraseña", type="password", placeholder="Repita contraseña")
                    
                    pwd_submitted = st.form_submit_button("🔑 Cambiar Contraseña", type="primary")
                    
                    if pwd_submitted:
                        if not new_password or len(new_password) < 6:
                            alert("La contraseña debe tener al menos 6 caracteres", type="error")
                        elif new_password != new_password_confirm:
                            alert("Las contraseñas no coinciden", type="error")
                        else:
                            try:
                                change_password(selected_username, new_password)
                                alert("Contraseña actualizada exitosamente", type="success")
                            except Exception as e:
                                alert(f"Error: {str(e)}", type="error")
            
            st.markdown("---")
            st.markdown("#### 🗑️ Eliminar Usuario")
            if st.button(f"❌ Eliminar usuario '{selected_username}'", key="delete_user_btn"):
                st.session_state.show_delete_user_modal = True
                st.session_state.delete_user_name = selected_username
                st.rerun()
            
            # Check if delete modal should be shown
            if st.session_state.get("show_delete_user_modal", False) and st.session_state.get("delete_user_name") == selected_username:
                show_delete_user_modal(selected_username)
    
    except Exception as e:
        alert(f"Error al cargar usuarios: {str(e)}", type="error")


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
            st.dataframe(df_logs, width='stretch', hide_index=True)
        else:
            alert("No hay registros de auditoría", type="info")



@st.dialog("⚠️ Confirmar Eliminación de Usuario", width="large")
def show_delete_user_modal(username: str):
    """Show modal to confirm user deletion"""
    st.markdown(f"""
    <div style='
        background-color: #ffebee;
        border-left: 4px solid #ef5350;
        padding: 16px;
        border-radius: 6px;
        color: #212121;
        font-size: 16px;
    '>
        ¿Está seguro de que desea eliminar el usuario "<b>{username}</b>"?
        <br><br>
        Esta acción es <b>irreversible</b> y no podrá restaurarse.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Sí, eliminar", type="primary", use_container_width=True):
            try:
                delete_user(username)
                st.toast(f"✅ Usuario '{username}' eliminado correctamente", icon="✅")
                st.session_state.show_delete_user_modal = False
                st.session_state.delete_user_name = None
                st.rerun()
            except Exception as e:
                alert(f"Error al eliminar: {str(e)}", type="error")
    
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.show_delete_user_modal = False
            st.rerun()
