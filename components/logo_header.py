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
    Render the professional logo header section using Streamlit columns.
    
    Includes:
    - Centered container with Streamlit columns
    - Purple crown icon (SVG)
    - Linear brain illustration with gradient (SVG)
    - Title and subtitle text
    """
    
    # SVG Brain illustration with pink-purple gradient
    brain_svg = """
    <svg viewBox="0 0 200 160" width="100" height="80" xmlns="http://www.w3.org/2000/svg" style="display: block; margin: 0 auto;">
        <defs>
            <linearGradient id="brainGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#f39ac8;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#9320d6;stop-opacity:1" />
            </linearGradient>
        </defs>
        
        <!-- Brain outline -->
        <path d="M 50 80 Q 50 40 100 40 Q 150 40 150 80" fill="none" stroke="url(#brainGradient)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        
        <!-- Left hemisphere -->
        <path d="M 75 50 Q 60 60 60 80 Q 60 100 75 110" fill="none" stroke="url(#brainGradient)" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M 80 55 Q 70 70 70 85" fill="none" stroke="url(#brainGradient)" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
        
        <!-- Right hemisphere -->
        <path d="M 125 50 Q 140 60 140 80 Q 140 100 125 110" fill="none" stroke="url(#brainGradient)" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M 120 55 Q 130 70 130 85" fill="none" stroke="url(#brainGradient)" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
        
        <!-- Central structure -->
        <circle cx="100" cy="85" r="8" fill="url(#brainGradient)" opacity="0.4"/>
        
        <!-- Bottom curves (cerebellum suggestion) -->
        <path d="M 85 110 Q 100 120 115 110" fill="none" stroke="url(#brainGradient)" stroke-width="2" stroke-linecap="round"/>
        <path d="M 90 115 Q 100 122 110 115" fill="none" stroke="url(#brainGradient)" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
    </svg>
    """
    
    # Crown SVG icon
    crown_svg = """
    <svg viewBox="0 0 100 100" width="28" height="28" xmlns="http://www.w3.org/2000/svg" style="display: inline-block;">
        <defs>
            <linearGradient id="crownGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#9320d6;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#3d0c4d;stop-opacity:1" />
            </linearGradient>
        </defs>
        
        <!-- Crown base -->
        <path d="M 15 65 L 20 35 L 35 50 L 50 25 L 65 50 L 80 35 L 85 65 Z" 
              fill="url(#crownGradient)" stroke="#9320d6" stroke-width="2"/>
        
        <!-- Bottom band -->
        <rect x="15" y="65" width="70" height="12" rx="2" fill="#9320d6" opacity="0.3"/>
        
        <!-- Jewels -->
        <circle cx="35" cy="42" r="4" fill="#f39ac8"/>
        <circle cx="50" cy="28" r="5" fill="#f39ac8"/>
        <circle cx="65" cy="42" r="4" fill="#f39ac8"/>
    </svg>
    """
    
    # Create container with columns
    col1, col2, col3 = st.columns([0.15, 0.7, 0.15])
    
    with col1:
        st.markdown(crown_svg, unsafe_allow_html=True)
    
    with col2:
        # Brain illustration
        st.markdown(brain_svg, unsafe_allow_html=True)
        
        # Title
        st.markdown(
            """
            <div style="text-align: center; margin-top: 0.5rem;">
                <h1 style="font-size: 2.5rem; font-weight: 700; color: #3d0c4d; margin: 0.5rem 0 0 0; letter-spacing: -1px;">
                    Cognidata
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Subtitle
        st.markdown(
            """
            <div style="text-align: center; margin-top: 0rem;">
                <p style="font-size: 0.95rem; color: #9320d6; margin: 0; font-weight: 500; letter-spacing: 0.5px;">
                    Evaluación Neuropsicológica
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.empty()
    
    # Divider
    st.divider()


if __name__ == "__main__":
    # Test the logo header
    render_logo_header()
    st.write("Logo header rendered successfully!")

