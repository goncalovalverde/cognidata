"""
Protocolos Page - Manage neuropsychological test protocols
"""

import streamlit as st
from datetime import datetime
from database.connection import SessionLocal
from services.protocol_service import protocol_service
from models import Protocol
from utils.colors import COLORS
from services.audit import audit_service


def render():
    """Render the protocols management page"""
    st.header("📋 Gestión de Protocolos")
    st.markdown("Crea y gestiona protocolos de evaluación neuropsicológica reutilizables")
    st.markdown("---")
    
    # Initialize session state for UI
    if "show_new_protocol" not in st.session_state:
        st.session_state.show_new_protocol = False
    if "editing_protocol" not in st.session_state:
        st.session_state.editing_protocol = None
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📊 Ver Protocolos", "➕ Crear Protocolo", "✏️ Editar Protocolo"])
    
    # TAB 1: View Protocols
    with tab1:
        _render_view_protocols()
    
    # TAB 2: Create Protocol
    with tab2:
        _render_create_protocol()
    
    # TAB 3: Edit Protocol
    with tab3:
        _render_edit_protocol()


def _render_view_protocols():
    """Render list of all protocols"""
    st.subheader("Protocolos Disponibles")
    
    # Get all protocols
    protocols = protocol_service.list_protocols()
    categories = protocol_service.list_categories()
    
    if not protocols:
        st.info("📭 No hay protocolos definidos aún. Crea uno en la pestaña '➕ Crear Protocolo'")
        return
    
    # Filter by category
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_category = st.selectbox(
            "Filtrar por categoría",
            ["Todos"] + categories,
            key="category_filter"
        )
    
    # Filter protocols
    filtered_protocols = protocols
    if selected_category != "Todos":
        filtered_protocols = [p for p in protocols if p.category == selected_category]
    
    # Display protocols as cards
    if not filtered_protocols:
        st.warning(f"No hay protocolos en la categoría '{selected_category}'")
        return
    
    # Create table view
    data = []
    for protocol in filtered_protocols:
        tests_list = ", ".join([t.test_type for t in protocol.get_tests_ordered()])
        data.append({
            "Nombre": protocol.name,
            "Categoría": protocol.category or "—",
            "Nº Testes": len(protocol.tests),
            "Testes": tests_list,
            "Creado": protocol.created_at.strftime("%d/%m/%Y") if protocol.created_at else "—",
            "ID": protocol.id
        })
    
    # Display as expandable sections instead of table
    st.markdown("#### Protocolos:")
    for i, protocol in enumerate(filtered_protocols):
        with st.expander(f"🧪 **{protocol.name}** ({len(protocol.tests)} testes)", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Categoría:** {protocol.category or '—'}")
                if protocol.description:
                    st.markdown(f"**Descripción:** {protocol.description}")
                
                st.markdown("**Testes incluidos:**")
                tests_ordered = protocol.get_tests_ordered()
                for idx, test in enumerate(tests_ordered, 1):
                    st.caption(f"  {idx}. {test.test_type}")
                
                st.caption(f"Creado: {protocol.created_at.strftime('%d/%m/%Y %H:%M') if protocol.created_at else '—'}")
            
            with col2:
                st.markdown("")
                st.markdown("")
                # Action buttons
                col_edit, col_del = st.columns(2)
                
                with col_edit:
                    if st.button("✏️ Editar", key=f"edit_{protocol.id}"):
                        st.session_state.editing_protocol = protocol.id
                        st.rerun()
                
                with col_del:
                    if st.button("🗑️ Eliminar", key=f"del_{protocol.id}"):
                        if _confirm_delete_protocol(protocol):
                            st.rerun()


def _render_create_protocol():
    """Render form to create new protocol"""
    st.subheader("Crear Nuevo Protocolo")
    
    with st.form("create_protocol_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nombre del Protocolo",
                placeholder="e.g., Rastreio Cognitivo",
                help="Nombre único del protocolo"
            )
        
        with col2:
            category = st.text_input(
                "Categoría",
                placeholder="e.g., Rastreio, Avaliação Completa",
                help="Categoría para organizar protocolos"
            )
        
        description = st.text_area(
            "Descripción",
            placeholder="Describir para qué se utiliza este protocolo...",
            height=80,
            help="Descripción opcional del propósito del protocolo"
        )
        
        st.markdown("#### Selecciona testes para el protocolo")
        
        # Get available tests
        available_tests = protocol_service.get_available_tests()
        
        # Multi-select for tests
        selected_tests = st.multiselect(
            "Testes a incluir",
            options=available_tests,
            help="Selecciona los testes que incluirá este protocolo"
        )
        
        # Reorder tests
        if selected_tests:
            st.markdown("**Orden de ejecución:**")
            test_order = {}
            
            cols = st.columns(len(selected_tests))
            for idx, test in enumerate(selected_tests):
                with cols[idx]:
                    order = st.number_input(
                        f"{test}",
                        min_value=1,
                        max_value=len(selected_tests),
                        value=idx + 1,
                        key=f"order_{test}"
                    )
                    test_order[test] = order
            
            # Sort tests by order
            selected_tests = sorted(selected_tests, key=lambda t: test_order[t])
        
        st.markdown("---")
        
        submitted = st.form_submit_button(
            "💾 Guardar Protocolo",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not name:
                st.error("❌ El nombre del protocolo es obligatorio")
            elif not selected_tests:
                st.error("❌ Debes seleccionar al menos un teste")
            else:
                try:
                    protocol = protocol_service.create_protocol(
                        name=name,
                        description=description,
                        category=category if category else None,
                        tests=selected_tests
                    )
                    
                    audit_service.log(
                        action="protocol.create",
                        resource_type="protocol",
                        resource_id=protocol.id,
                        details={"name": name, "test_count": len(selected_tests)}
                    )
                    
                    st.success(f"✅ Protocolo '{name}' creado con éxito")
                    st.balloons()
                    st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error al crear protocolo: {str(e)}")


def _render_edit_protocol():
    """Render form to edit existing protocol"""
    st.subheader("Editar Protocolo")
    
    protocols = protocol_service.list_protocols()
    if not protocols:
        st.info("📭 No hay protocolos para editar")
        return
    
    # Select protocol to edit
    protocol_names = {p.name: p.id for p in protocols}
    selected_name = st.selectbox(
        "Selecciona protocolo a editar",
        options=list(protocol_names.keys()),
        key="edit_protocol_select"
    )
    
    if not selected_name:
        return
    
    protocol_id = protocol_names[selected_name]
    protocol = protocol_service.get_protocol(protocol_id)
    
    if not protocol:
        st.error("❌ Protocolo no encontrado")
        return
    
    # Display current protocol info
    st.markdown("#### Protocolo Actual")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"**Categoría:** {protocol.category or '—'}")
    with col2:
        st.caption(f"**Testes:** {len(protocol.tests)}")
    
    current_tests = [t.test_type for t in protocol.get_tests_ordered()]
    st.caption(f"**Orden actual:** {', '.join(current_tests)}")
    
    st.markdown("---")
    
    # Edit form
    with st.form("edit_protocol_form"):
        name = st.text_input(
            "Nombre del Protocolo",
            value=protocol.name,
            help="Cambiar nombre"
        )
        
        category = st.text_input(
            "Categoría",
            value=protocol.category or "",
            help="Cambiar categoría"
        )
        
        description = st.text_area(
            "Descripción",
            value=protocol.description or "",
            height=80,
            help="Cambiar descripción"
        )
        
        st.markdown("#### Testes del Protocolo")
        
        available_tests = protocol_service.get_available_tests()
        selected_tests = st.multiselect(
            "Testes a incluir",
            options=available_tests,
            default=current_tests,
            help="Modificar testes incluidos"
        )
        
        # Reorder tests
        if selected_tests:
            test_order = {}
            cols = st.columns(min(4, len(selected_tests)))
            for idx, test in enumerate(selected_tests):
                with cols[idx % len(cols)]:
                    order = st.number_input(
                        f"{test}",
                        min_value=1,
                        max_value=len(selected_tests),
                        value=idx + 1,
                        key=f"edit_order_{test}"
                    )
                    test_order[test] = order
            
            selected_tests = sorted(selected_tests, key=lambda t: test_order[t])
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button(
                "💾 Guardar Cambios",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            deleted = st.form_submit_button(
                "🗑️ Eliminar Protocolo",
                use_container_width=True
            )
        
        if submitted:
            if not name:
                st.error("❌ El nombre es obligatorio")
            elif not selected_tests:
                st.error("❌ Debes tener al menos un teste")
            else:
                try:
                    updated = protocol_service.update_protocol(
                        protocol_id=protocol_id,
                        name=name,
                        description=description,
                        category=category if category else None,
                        tests=selected_tests
                    )
                    
                    audit_service.log(
                        action="protocol.update",
                        resource_type="protocol",
                        resource_id=protocol_id,
                        details={"name": name}
                    )
                    
                    st.success(f"✅ Protocolo actualizado")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if deleted:
            if _confirm_delete_protocol(protocol):
                st.rerun()


def _confirm_delete_protocol(protocol: Protocol) -> bool:
    """Confirm deletion of protocol"""
    if st.session_state.get(f"confirm_delete_{protocol.id}"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirmar eliminación", key=f"confirm_yes_{protocol.id}"):
                protocol_service.delete_protocol(protocol.id)
                
                audit_service.log(
                    action="protocol.delete",
                    resource_type="protocol",
                    resource_id=protocol.id,
                    details={"name": protocol.name}
                )
                
                st.success(f"✅ Protocolo '{protocol.name}' eliminado")
                st.session_state[f"confirm_delete_{protocol.id}"] = False
                return True
        
        with col2:
            if st.button("❌ Cancelar", key=f"confirm_no_{protocol.id}"):
                st.session_state[f"confirm_delete_{protocol.id}"] = False
                st.rerun()
        
        return False
    
    if st.button(f"⚠️ ¿Eliminar '{protocol.name}'?", key=f"delete_confirm_{protocol.id}"):
        st.session_state[f"confirm_delete_{protocol.id}"] = True
        st.rerun()
    
    return False
