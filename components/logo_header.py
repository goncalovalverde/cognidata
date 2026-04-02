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
    Compact version to save sidebar space.
    
    Includes:
    - Brain illustration (emoji)
    - Title "Cognidata"
    - Subtitle "Evaluación Neuropsicológica"
    """
    
    # Simple centered layout using columns
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    
    with col2:
        # Brain emoji and title together with negative margin to reduce gap
        st.markdown("""
        <div style="text-align: center; line-height: 0.8;">
            <div style="font-size: 2.5rem;">🧠</div>
            <h1 style="color: #3d0c4d; font-size: 1.8rem; margin: -0.5rem 0 0.1rem 0; letter-spacing: -0.5px; font-weight: 700;">
                Cognidata
            </h1>
            <p style="color: #9320d6; font-size: 0.85rem; margin: 0; font-weight: 500; letter-spacing: 0.3px;">
                Evaluación Neuropsicológica
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Minimal divider
    st.divider()


if __name__ == "__main__":
    # Test the logo header
    render_logo_header()
    st.write("Logo header rendered successfully!")

