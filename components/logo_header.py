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
    Render the professional logo header section.
    
    Includes:
    - Centered container
    - Purple crown icon (top-left)
    - Linear brain illustration with gradient
    - Title and subtitle text
    """
    
    # SVG Brain illustration with pink-purple gradient
    brain_svg = """
    <svg viewBox="0 0 200 160" width="120" height="96" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="brainGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:rgb(243,150,200);stop-opacity:1" />
                <stop offset="100%" style="stop-color:rgb(147,32,214);stop-opacity:1" />
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
    <svg viewBox="0 0 100 100" width="32" height="32" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="crownGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:rgb(147,32,214);stop-opacity:1" />
                <stop offset="100%" style="stop-color:rgb(61,12,77);stop-opacity:1" />
            </linearGradient>
        </defs>
        
        <!-- Crown base -->
        <path d="M 15 65 L 20 35 L 35 50 L 50 25 L 65 50 L 80 35 L 85 65 Z" 
              fill="url(#crownGradient)" stroke="rgb(147,32,214)" stroke-width="2"/>
        
        <!-- Bottom band -->
        <rect x="15" y="65" width="70" height="12" rx="2" fill="rgb(147,32,214)" opacity="0.3"/>
        
        <!-- Jewels -->
        <circle cx="35" cy="42" r="4" fill="rgb(243,150,200)"/>
        <circle cx="50" cy="28" r="5" fill="rgb(243,150,200)"/>
        <circle cx="65" cy="42" r="4" fill="rgb(243,150,200)"/>
    </svg>
    """
    
    # Main logo header HTML/CSS
    logo_html = f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, rgba(249, 247, 249, 0.8) 0%, rgba(243, 222, 241, 0.5) 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        position: relative;
        border: 1px solid rgba(147, 32, 214, 0.1);
    ">
        <!-- Crown icon (top-left) -->
        <div style="
            position: absolute;
            top: 1rem;
            left: 1rem;
            opacity: 0.85;
        ">
            {crown_svg}
        </div>
        
        <!-- Brain illustration -->
        <div style="
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: center;
        ">
            {brain_svg}
        </div>
        
        <!-- Main title -->
        <h1 style="
            font-size: 3rem;
            font-weight: 700;
            color: rgb(61, 12, 77);
            margin: 0;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
            font-family: 'Playfair Display', serif;
        ">
            Cognidata
        </h1>
        
        <!-- Subtitle -->
        <p style="
            font-size: 1rem;
            color: rgb(147, 32, 214);
            margin: 0;
            font-weight: 500;
            font-family: 'Montserrat', sans-serif;
            letter-spacing: 0.5px;
        ">
            Evaluación Neuropsicológica
        </p>
    </div>
    """
    
    st.markdown(logo_html, unsafe_allow_html=True)


if __name__ == "__main__":
    # Test the logo header
    render_logo_header()
    st.write("Logo header rendered successfully!")
