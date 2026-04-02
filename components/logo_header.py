"""
Logo header component for CogniData with brain illustration and branding.

Features:
- Centered logo block
- Brain illustration with pink-purple gradient
- Main title (Cognidata)
- Subtitle (Evaluación Neuropsicológica)
- Crown icon in top-left corner
"""

import streamlit as st


def render_logo_header():
    """
    Render the professional logo header section using Streamlit components.
    
    Includes:
    - Brain illustration (emoji styled)
    - Title "Cognidata"
    - Subtitle "Evaluación Neuropsicológica"
    """
    
    # Simple centered layout using columns
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    
    with col2:
        # Crown emoji at top
        st.markdown("""
        <div style="text-align: center; font-size: 1.5rem; margin-bottom: 0.5rem;">
            👑
        </div>
        """, unsafe_allow_html=True)
        
        # Brain emoji (centered, larger)
        st.markdown("""
        <div style="text-align: center; font-size: 4rem; margin: 0.5rem 0;">
            🧠
        </div>
        """, unsafe_allow_html=True)
        
        # Title
        st.markdown("""
        <h1 style="text-align: center; color: #3d0c4d; font-size: 2.5rem; margin: 0.5rem 0; letter-spacing: -1px; font-weight: 700;">
            Cognidata
        </h1>
        """, unsafe_allow_html=True)
        
        # Subtitle
        st.markdown("""
        <p style="text-align: center; color: #9320d6; font-size: 1rem; margin: 0; font-weight: 500; letter-spacing: 0.5px;">
            Evaluación Neuropsicológica
        </p>
        """, unsafe_allow_html=True)
    
    # Divider
    st.divider()


if __name__ == "__main__":
    # Test the logo header
    render_logo_header()
    st.write("Logo header rendered successfully!")

