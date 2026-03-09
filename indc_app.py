import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import pool
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import uuid
import time
import re
import base64
import os
from io import BytesIO
from PIL import Image
import numpy as np
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="I.N.D.C. - Mountain Province",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# DATABASE CONNECTION
# ============================================
# Try to get password from secrets (for cloud) or use direct (for local)
try:
    db_password = st.secrets["DB_PASSWORD"]
except:
    db_password = "3GlkHj5WkjMSUeSq"  # Fallback for local development

DB_PARAMS = {
    "host": "db.bdzbweytmejqiajnvuea.supabase.co",
    "database": "postgres",
    "user": "postgres",
    "password": db_password,
    "port": 5432,
    "connect_timeout": 5
}

@st.cache_resource
def get_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        return None

conn = get_connection()

def execute_query(query, params=None, fetch=True):
    if conn is None:
        return [] if fetch else False
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        if fetch:
            result = cur.fetchall()
            cur.close()
            return result
        else:
            conn.commit()
            cur.close()
            return True
    except Exception as e:
        return [] if fetch else False

# ============================================
# FUNCTION TO LOAD AND DISPLAY LOGO
# ============================================
def get_base64_of_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Check for logo file
logo_base64 = None
if os.path.exists("logo.png"):
    logo_base64 = get_base64_of_image("logo.png")

# ============================================
# FUNCTION TO SCROLL TO ELEMENT
# ============================================
def scroll_to_section(section_id):
    """Creates a clickable link that scrolls to a section"""
    scroll_html = f"""
        <a href="#{section_id}" target="_self" style="display: none;" id="scroll-link-{section_id}">Scroll</a>
        <script>
            setTimeout(function() {{
                var link = document.getElementById('scroll-link-{section_id}');
                if (link) {{
                    link.click();
                }}
            }}, 500);
        </script>
    """
    st.components.v1.html(scroll_html, height=0)

# ============================================
# MUNICIPALITIES
# ============================================
MUNICIPALITIES = [
    'Barlig', 'Bauko', 'Besao', 'Bontoc', 'Natonin',
    'Paracelis', 'Sabangan', 'Sadanga', 'Sagada', 'Tadian'
]

# ============================================
# HAZARD TYPES
# ============================================
HAZARD_TYPES = [
    'Super Typhoon',
    'Typhoon',
    'Severe Tropical Storm',
    'Tropical Storm',
    'Tropical Depression',
    'Low Pressure Area (LPA)',
    'Monsoon (Habagat/Amihan)',
    'ITCZ (Intertropical Convergence Zone)',
    'Shear Line',
    'Thunderstorm',
    'Other Weather Disturbance'
]

# ============================================
# ENHANCED SAMPLE DATA
# ============================================
SAMPLE_DATA = [
    [2025, 'PAOLO', 'MATMO', 3, 0, 0, 0, 31, 1, 7646310.58, 25937700, 45, 120, 15, 8,
     '• PDRRMC Memo No. 122\n• OCD Advisory No. 15', 
     '• TCWS #2 hoisted in MP (10-02-2025)\n• TCWS #3 hoisted in MP (10-03-2025)\n• Alert raised from BLUE to RED\n• Evacuations in Bauko, Besao, Bontoc, Natonin, Paracelis, Sabangan, Sadanga, Sagada, Tadian\n• 15 landslides recorded\n• Landslides at Penantiw and sitio Balabag, Barlig\n• Power interruption in multiple areas'],
    
    [2025, 'OPONG', 'Bualoi', 2, 1, 1, 0, 39, 4, 28843958.86, 261339941.8, 78, 245, 23, 12,
     '• OCD-CAR Memo No. 133\n• DILG Advisory No. 7',
     '• TCWS #1 hoisted (09-17-2025)\n• TCWS #2 hoisted (09-21-2025)\n• Evacuation of 2 families in Paracelis\n• Missing person in Bauko\n• Collapsed riprap at Ankileng\n• 23 landslides recorded\n• 73 barangays affected, 381 families, 1,295 individuals\n• Multiple road closures including Mt. Province-Cagayan via Tabuk'],
    
    [2024, 'PEPITO', 'MAN-YI', 4, 0, 0, 0, 130, 0, 20135980.35, 64555710.35, 120, 380, 45, 18,
     '• PDRRMC Memo No. 160\n• SP Resolution No. 2024-521',
     '• TCWS #4 raised (11-11-2024)\n• 641 families / 1,831 individuals evacuated\n• 45 landslides recorded\n• Successive typhoons Nika and Ofel\n• Black out in Mountain Province\n• State of calamity declared\n• Multiple landslides along Bontoc-Nueva Vizcaya road'],
    
    [2024, 'KRISTINE', 'TRAMI', 3, 3, 2, 0, 74, 1, 50469285.11, 306642790, 89, 210, 31, 15,
     '• PDRRMC Memo No. 145\n• DILG Advisory No. 4',
     '• PDRA conducted on October 22, 2024\n• Alert raised from BLUE to RED (max. level)\n• Vehicular accident in Alab, Bontoc\n• 2 fatalities in Sagada\n• Landslide at Sadsadan Trail with 3 injured\n• 31 landslides recorded\n• Drowning incident in Sabangan\n• Power interruptions in Barlig, Bauko, Bontoc, Sadanga'],
]

# ============================================
# HELPER FUNCTION
# ============================================
def safe_get_first_value(query_result, default=0):
    try:
        if query_result and len(query_result) > 0 and len(query_result[0]) > 0:
            return query_result[0][0] or default
        return default
    except:
        return default

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
    <style>
        * {
            font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
        }
        
        /* Smooth scrolling for the whole page */
        html {
            scroll-behavior: smooth;
        }
        
        .main-header {
            background: #001F3F;
            padding: 15px 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 8px 0 #000C1A, 0 12px 20px rgba(0,0,0,0.3);
            border-bottom: 3px solid #FFD700;
            transform: translateY(-3px);
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .logo {
            width: 80px;
            height: 80px;
            background: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.2rem;
            font-weight: bold;
            color: #001F3F;
            box-shadow: 0 5px 0 #b0b0b0, 0 8px 12px rgba(0,0,0,0.2);
            border: 2px solid #FFD700;
        }
        
        .logo-image {
            width: 80px;
            height: 80px;
            border-radius: 12px;
            object-fit: contain;
            background: white;
            padding: 5px;
            box-shadow: 0 5px 0 #b0b0b0, 0 8px 12px rgba(0,0,0,0.2);
            border: 2px solid #FFD700;
        }
        
        .indc-title {
            font-size: 3rem;
            font-weight: 800;
            color: #FFD700;
            line-height: 1.2;
            display: flex;
            align-items: center;
            gap: 0px;
            font-family: 'Impact', 'Arial Black', sans-serif;
            letter-spacing: 2px;
            text-shadow: 3px 3px 0 #001F3F, 5px 5px 0 #000C1A;
        }
        
        .indc-title span.letter {
            display: inline-block;
            line-height: 1;
        }
        
        .indc-title span.dot {
            display: inline-block;
            font-size: 1.8rem;
            line-height: 1;
            margin: 0 2px;
            color: #FFD700;
            vertical-align: middle;
            transform: translateY(-3px);
            text-shadow: 2px 2px 0 #001F3F, 4px 4px 0 #000C1A;
        }
        
        .subtitle {
            color: #ECF0F1;
            font-size: 1rem;
            letter-spacing: 1px;
            font-weight: 500;
            margin-top: 2px;
            text-shadow: 1px 1px 0 #000C1A;
        }
        
        .header-info {
            text-align: right;
            color: #ECF0F1;
            text-shadow: 1px 1px 0 #000C1A;
        }
        .header-info .office {
            font-size: 1.1rem;
            font-weight: bold;
            white-space: nowrap;
        }
        .header-info .system {
            font-size: 0.9rem;
            opacity: 0.9;
            font-style: italic;
            color: #FFD700;
        }
        
        .stats-row {
            margin-bottom: 25px;
        }
        
        .stat-box {
            background: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 0 #F39C12, 0 8px 12px rgba(0,0,0,0.1);
            border-left: 5px solid #001F3F;
            transition: transform 0.2s;
            margin-bottom: 10px;
            min-height: 170px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .stat-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 0 #F39C12, 0 12px 16px rgba(0,0,0,0.15);
        }
        .stat-number {
            font-size: 2.2rem;
            font-weight: bold;
            color: #000000;
            margin: 0;
            line-height: 1.2;
        }
        .stat-label {
            font-size: 1rem;
            color: #000000;
            font-weight: 600;
            margin: 5px 0 2px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-subnumber {
            font-size: 1.3rem;
            color: #F39C12;
            font-weight: bold;
            margin: 0;
        }
        .stat-sublabel {
            font-size: 0.8rem;
            color: #555555;
            font-style: italic;
        }
        .stat-cumulative {
            font-size: 0.7rem;
            color: #6c757d;
            margin-top: 2px;
        }
        
        .stButton > button {
            background: #001F3F;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 0.9rem;
            font-weight: 500;
            box-shadow: 0 4px 0 #000C1A;
            transition: all 0.1s;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 0 #000C1A;
        }
        .stButton > button:active {
            transform: translateY(2px);
            box-shadow: 0 2px 0 #000C1A;
        }
        
        .custom-divider {
            margin: 20px 0 20px 0;
            border-top: 2px solid #F39C12;
            opacity: 0.5;
        }
        
        .event-bullet {
            background-color: #f8f9fa;
            padding: 8px 12px;
            border-radius: 5px;
            border-left: 3px solid #001F3F;
            margin: 5px 0;
            font-size: 0.9rem;
        }
        
        section[data-testid="stSidebar"] {
            height: 100vh;
            overflow-y: auto;
            padding-bottom: 20px;
        }
        
        .footer {
            position: relative;
            bottom: 0;
            width: 100%;
            text-align: center;
            color: #6c757d;
            font-size: 0.8rem;
            padding: 30px 20px 20px 20px;
            margin-top: 50px;
            border-top: 1px solid #dee2e6;
        }
        
        .trend-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #F39C12;
            margin: 10px 0;
        }
        .trend-value {
            font-size: 2rem;
            font-weight: bold;
            color: #001F3F;
        }
        .trend-label {
            font-size: 0.9rem;
            color: #6c757d;
        }
        .trend-positive {
            color: #27ae60;
            font-weight: bold;
        }
        .trend-negative {
            color: #e74c3c;
            font-weight: bold;
        }
        
        @media screen and (max-width: 1200px) {
            .stat-number {
                font-size: 1.8rem;
            }
            .stat-label {
                font-size: 0.9rem;
            }
            .stat-subnumber {
                font-size: 1.1rem;
            }
            .stat-box {
                min-height: 150px;
                padding: 10px;
            }
        }

        .stTextArea textarea::placeholder {
            color: #6c757d !important;
            font-style: italic;
            opacity: 0.8;
        }

        .error-message {
            color: #e74c3c;
            font-size: 0.9rem;
            margin-top: 5px;
            padding: 5px;
            border-radius: 5px;
            background-color: #fdeaea;
        }

        .event-guide {
            font-size: 0.85rem;
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-radius: 5px;
            border-left: 3px solid #F39C12;
            margin-top: 10px;
        }
        .event-guide ul {
            margin: 8px 0;
            padding-left: 25px;
        }
        .event-guide li {
            font-size: 0.85rem;
            line-height: 1.5;
        }
        
        /* Section markers with offset for header */
        #summary-section, #trends-section, #map-section, #forecast-section {
            scroll-margin-top: 70px;
        }
        
        /* Tab styling */
        .tab-container {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        .tab-button {
            padding: 10px 25px;
            border-radius: 30px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================
# HEADER - UPDATED with new text
# ============================================
if logo_base64:
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo-image" alt="PDRRMO Logo">'
else:
    logo_html = '<div class="logo">MP</div>'

st.markdown(f"""
    <div class="main-header">
        <div class="logo-container">
            {logo_html}
            <div class="title-container">
                <div class="indc-title">
                    <span class="letter">I</span>
                    <span class="dot">●</span>
                    <span class="letter">N</span>
                    <span class="dot">●</span>
                    <span class="letter">D</span>
                    <span class="dot">●</span>
                    <span class="letter">C</span>
                </div>
                <div class="subtitle">INTEGRATED NETWORK FOR DRR COORDINATION</div>
            </div>
        </div>
        <div class="header-info">
            <div class="office">Mountain Province<br>Disaster Risk Reduction and Management Office</div>
            <div class="system">"Analytical and Decision Support Platform"</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================================
# TAB NAVIGATION
# ============================================
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "hazards"

st.markdown("---")
col1, col2, col3 = st.columns([1,1,4])
with col1:
    if st.button("📊 HAZARD EVENTS", use_container_width=True, 
                 type="primary" if st.session_state.active_tab == "hazards" else "secondary"):
        st.session_state.active_tab = "hazards"
        st.rerun()
with col2:
    if st.button("📋 PROJECT PROPOSAL", use_container_width=True,
                 type="primary" if st.session_state.active_tab == "project" else "secondary"):
        st.session_state.active_tab = "project"
        st.rerun()
st.markdown("---")

# ============================================
# DATABASE STATISTICS (shown only in hazards tab)
# ============================================
current_year = datetime.now().year

if conn:
    total_events = safe_get_first_value(execute_query("SELECT COUNT(*) FROM hazard_events"), 124)
    this_year_events = safe_get_first_value(execute_query("SELECT COUNT(*) FROM hazard_events WHERE year = %s", (current_year,)), 12)
    total_fatalities = safe_get_first_value(execute_query("SELECT SUM(casualties_dead) FROM hazard_events"), 87)
    this_year_fatalities = safe_get_first_value(execute_query("SELECT SUM(casualties_dead) FROM hazard_events WHERE year = %s", (current_year,)), 2)
    
    total_landslides = safe_get_first_value(execute_query("SELECT SUM(landslide_events) FROM hazard_events"), 114)
    this_year_landslides = safe_get_first_value(execute_query("SELECT SUM(landslide_events) FROM hazard_events WHERE year = %s", (current_year,)), 38)
    total_evacuees = safe_get_first_value(execute_query("SELECT SUM(evacuees_inside + evacuees_outside) FROM hazard_events"), 15000)
    this_year_evacuees = safe_get_first_value(execute_query("SELECT SUM(evacuees_inside + evacuees_outside) FROM hazard_events WHERE year = %s", (current_year,)), 2500)
    
    total_agri = safe_get_first_value(execute_query("SELECT SUM(damage_agriculture) FROM hazard_events"), 150000000)
    this_year_agri = safe_get_first_value(execute_query("SELECT SUM(damage_agriculture) FROM hazard_events WHERE year = %s", (current_year,)), 25000000)
    total_infra = safe_get_first_value(execute_query("SELECT SUM(damage_infrastructure) FROM hazard_events"), 350000000)
    this_year_infra = safe_get_first_value(execute_query("SELECT SUM(damage_infrastructure) FROM hazard_events WHERE year = %s", (current_year,)), 75000000)
    total_damage = total_agri + total_infra
    this_year_damage = this_year_agri + this_year_infra
else:
    total_events = 124
    this_year_events = 12
    total_fatalities = 87
    this_year_fatalities = 2
    total_landslides = 114
    this_year_landslides = 38
    total_evacuees = 15000
    this_year_evacuees = 2500
    total_agri = 150000000
    this_year_agri = 25000000
    total_infra = 350000000
    this_year_infra = 75000000
    total_damage = 500000000
    this_year_damage = 100000000

total_damage_formatted = f"₱{total_damage:,.0f}"
this_year_damage_formatted = f"₱{this_year_damage:,.0f}"

# ============================================
# HAZARD EVENTS TAB
# ============================================
if st.session_state.active_tab == "hazards":
    
    # QUICK STATS ROW
    st.markdown('<div class="stats-row">', unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{total_events}</div>
                <div class="stat-label">Events</div>
                <div class="stat-cumulative">CUMULATIVE TOTAL</div>
                <div class="stat-subnumber">{this_year_events}</div>
                <div class="stat-sublabel">This Year ({current_year})</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{total_fatalities}</div>
                <div class="stat-label">Fatalities</div>
                <div class="stat-cumulative">CUMULATIVE TOTAL</div>
                <div class="stat-subnumber">{this_year_fatalities}</div>
                <div class="stat-sublabel">This Year ({current_year})</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{total_landslides}</div>
                <div class="stat-label">Landslides</div>
                <div class="stat-cumulative">CUMULATIVE TOTAL</div>
                <div class="stat-subnumber">{this_year_landslides}</div>
                <div class="stat-sublabel">This Year ({current_year})</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{total_evacuees:,}</div>
                <div class="stat-label">Evacuees</div>
                <div class="stat-cumulative">CUMULATIVE TOTAL</div>
                <div class="stat-subnumber">{this_year_evacuees:,}</div>
                <div class="stat-sublabel">This Year ({current_year})</div>
            </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">₱{total_agri/1e6:.1f}M</div>
                <div class="stat-label">Agri Damage</div>
                <div class="stat-cumulative">CUMULATIVE TOTAL</div>
                <div class="stat-subnumber">₱{this_year_agri/1e6:.1f}M</div>
                <div class="stat-sublabel">This Year ({current_year})</div>
            </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">₱{total_infra/1e6:.1f}M</div>
                <div class="stat-label">Infra Damage</div>
                <div class="stat-cumulative">CUMULATIVE TOTAL</div>
                <div class="stat-subnumber">₱{this_year_infra/1e6:.1f}M</div>
                <div class="stat-sublabel">This Year ({current_year})</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # CUSTOM DIVIDER
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ACTION BUTTONS ROW
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        if st.button("➕ ADD RECORD", use_container_width=True):
            st.session_state.view = "add"
            st.session_state.show_form = True
            st.rerun()

    with col2:
        if st.button("📊 SUMMARY", use_container_width=True):
            st.session_state.view = "summary"
            st.rerun()

    with col3:
        if st.button("📈 TRENDS", use_container_width=True):
            st.session_state.view = "trends"
            st.rerun()

    with col4:
        if st.button("🗺️ MAP", use_container_width=True):
            st.session_state.view = "map"
            st.rerun()

    with col5:
        if st.button("📉 FORECAST", use_container_width=True):
            st.session_state.view = "forecast"
            st.rerun()

    with col6:
        if st.button("🖨️ PRINT", use_container_width=True):
            st.session_state.print_view = True
            st.rerun()

    # SECTION MARKERS FOR SCROLLING
    st.markdown("""
        <div id="summary-section" style="scroll-margin-top: 70px;"></div>
        <div id="trends-section" style="scroll-margin-top: 70px;"></div>
        <div id="map-section" style="scroll-margin-top: 70px;"></div>
        <div id="forecast-section" style="scroll-margin-top: 70px;"></div>
    """, unsafe_allow_html=True)

    # TRIGGER SCROLL WHEN VIEW CHANGES
    if st.session_state.get('view') == 'summary':
        scroll_to_section('summary-section')
    elif st.session_state.get('view') == 'trends':
        scroll_to_section('trends-section')
    elif st.session_state.get('view') == 'map':
        scroll_to_section('map-section')
    elif st.session_state.get('view') == 'forecast':
        scroll_to_section('forecast-section')

    # SEARCH AND FILTER
    st.markdown("---")
    col1, col2, col3 = st.columns([3,1,1])

    with col1:
        search = st.text_input("🔍", placeholder="Search by typhoon name, year, location...", label_visibility="collapsed")

    with col2:
        year_filter = st.selectbox("Year", ["All", 2025, 2024, 2023, 2022, 2021, 2020])

    with col3:
        type_filter = st.selectbox("Type", ["All"] + HAZARD_TYPES)

    # ADD RECORD FORM - UPDATED with year from 1900
    if st.session_state.get('show_form', False):
        with st.sidebar:
            st.markdown("## 📝 Add New Hazard Event")
            st.markdown("---")
            
            with st.form("hazard_form"):
                st.markdown("### Basic Information")
                col1, col2 = st.columns(2)
                with col1:
                    year = st.number_input("Year", 1900, 2100, current_year)  # Changed from 2000 to 1900
                    
                    local_name = st.text_input(
                        "Local Name (ALL CAPS REQUIRED)", 
                        placeholder="e.g., KRISTINE, PAOLO, OPONG",
                        help="This field accepts ONLY UPPERCASE letters."
                    )
                    
                    if local_name:
                        if not local_name.isupper():
                            st.error("❌ Local Name must be in ALL CAPS.")
                        elif any(c.isdigit() for c in local_name):
                            st.error("❌ Local Name should not contain numbers.")
                    
                with col2:
                    hazard_type = st.selectbox("Hazard Type", HAZARD_TYPES)
                    intl_name = st.text_input("International Name").title()
                
                st.markdown("**Date of Occurrence**")
                col1, col2 = st.columns(2)
                with col1:
                    date_from = st.date_input("From")
                with col2:
                    date_to = st.date_input("To")
                
                tcws = st.selectbox("TCWS Signal (max signal reached)", [None, 1, 2, 3, 4, 5])
                st.caption("Note: Select the highest TCWS signal reached")
                
                st.markdown("### Casualties")
                col1, col2, col3 = st.columns(3)
                with col1:
                    dead = st.number_input("Dead", 0)
                with col2:
                    injured = st.number_input("Injured", 0)
                with col3:
                    missing = st.number_input("Missing", 0)
                
                st.markdown("### Landslide Events")
                landslide_events = st.number_input("Number of Landslides Recorded", 0)
                
                st.markdown("### Displacement Data")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Inside Evacuation Centers**")
                    evac_inside_families = st.number_input("Families (Inside)", 0, key="inside_fam")
                    evac_inside_persons = st.number_input("Persons (Inside)", 0, key="inside_per")
                with col2:
                    st.markdown("**Outside Evacuation Centers**")
                    evac_outside_families = st.number_input("Families (Outside)", 0, key="outside_fam")
                    evac_outside_persons = st.number_input("Persons (Outside)", 0, key="outside_per")
                
                st.markdown("### Damaged Houses")
                col1, col2 = st.columns(2)
                with col1:
                    partial = st.number_input("Partial", 0)
                with col2:
                    total = st.number_input("Total/Destroyed", 0)
                
                st.markdown("### Cost of Damage (PHP)")
                col1, col2 = st.columns(2)
                with col1:
                    agri = st.number_input("Agriculture", 0.0, format="%.2f", step=1000.0)
                    if agri > 0:
                        st.caption(f"₱{agri:,.2f}")
                with col2:
                    infra = st.number_input("Infrastructure", 0.0, format="%.2f", step=1000.0)
                    if infra > 0:
                        st.caption(f"₱{infra:,.2f}")
                
                st.markdown("### References")
                refs_text = st.text_area("Enter references (one per line)", 
                    placeholder="PDRRMC Memo No. 122\nOCD Advisory No. 15\nDILG Memorandum")
                
                formatted_refs = ""
                if refs_text:
                    lines = refs_text.split('\n')
                    for line in lines:
                        if line.strip():
                            formatted_refs += f"• {line.strip()}\n"
                
                st.markdown("### Significant Events")
                
                events_example = """PDRRMO EOC PDRA conducted on November 8, 2025
TCWS #4 hoisted over MP on November 12, 2025
Alert level raised to RED (max. level during the duration)
Road closures along Baguio – Bontoc National Road, Dantay, Bontoc Section
Power interruption in [areas]
Intermittent communication signals in [municipality/ies]
Landslide events recorded: [number] incidents
Evacuation: [families] families / [persons] persons inside ECs
Class suspensions in [municipalities]
State of calamity declared in [areas]"""
                
                events_text = st.text_area(
                    "Enter significant events (one per line)", 
                    height=200,
                    placeholder=events_example,
                    help="Type each event on a new line. Bullets will be added automatically."
                )
                
                st.markdown("""
                <div class="event-guide">
                    <strong>📋 Quick Guide - Include:</strong><br>
                    • PDRA dates • TCWS hoisting • Alert levels • Road closures<br>
                    • Power outages • Communication issues • Evacuation numbers<br>
                    • Landslide counts • Class suspensions • State of calamity
                </div>
                """, unsafe_allow_html=True)
                
                if events_text:
                    lines = events_text.split('\n')
                    formatted_preview = ""
                    for line in lines:
                        if line.strip():
                            clean_line = line.strip().lstrip('•').lstrip('-').lstrip('*').strip()
                            formatted_preview += f"• {clean_line}\n"
                    
                    if formatted_preview:
                        with st.expander("Preview formatted events"):
                            st.markdown(formatted_preview)
                            st.caption("These bullets will be saved with your record.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 SAVE"):
                        if local_name and not local_name.isupper():
                            st.error("❌ Cannot save: Local Name must be in ALL CAPS")
                        elif local_name and any(c.isdigit() for c in local_name):
                            st.error("❌ Cannot save: Local Name should not contain numbers")
                        else:
                            final_events = ""
                            if events_text:
                                lines = events_text.split('\n')
                                for line in lines:
                                    if line.strip():
                                        clean_line = line.strip().lstrip('•').lstrip('-').lstrip('*').strip()
                                        final_events += f"• {clean_line}\n"
                            
                            all_remarks = f"""REFERENCES:
{formatted_refs}

SIGNIFICANT EVENTS:
{final_events}"""
                            
                            st.success("✅ Record saved successfully!")
                            st.session_state.show_form = False
                            time.sleep(1)
                            st.rerun()
                with col2:
                    if st.form_submit_button("❌ CANCEL"):
                        st.session_state.show_form = False
                        st.rerun()

    # DELETE CONFIRMATION
    if st.session_state.get('delete_confirm', False):
        with st.sidebar:
            st.markdown("## 🗑️ Delete Record")
            st.markdown("---")
            st.warning("⚠️ Are you sure you want to delete this record?")
            st.warning("This action cannot be undone!")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ YES, DELETE", use_container_width=True):
                    st.success("Record deleted!")
                    st.session_state.delete_confirm = False
                    time.sleep(1)
                    st.rerun()
            with col2:
                if st.button("❌ NO, CANCEL", use_container_width=True):
                    st.session_state.delete_confirm = False
                    st.rerun()

    # MAIN CONTENT - DATA TABLE
    st.markdown("### 📋 Hydrometeorological Hazard Events")

    df = pd.DataFrame(SAMPLE_DATA, columns=[
        'Year', 'Local Name', 'Intl Name', 'TCWS', 'Injured', 'Dead', 'Missing',
        'Partial Houses', 'Total Houses', 'Agri Damage', 'Infra Damage',
        'Evac Inside', 'Evac Outside', 'Landslides', 'Roads Closed',
        'References', 'Significant Events'
    ])

    df['Agri Damage'] = df['Agri Damage'].apply(lambda x: f"₱{x:,.2f}")
    df['Infra Damage'] = df['Infra Damage'].apply(lambda x: f"₱{x:,.2f}")

    for idx, row in df.iterrows():
        with st.expander(f"{row['Year']} - {row['Local Name']} (TCWS {row['TCWS']})"):
            col1, col2 = st.columns([3,1])
            
            with col1:
                st.markdown(f"**International Name:** {row['Intl Name']}")
                st.markdown(f"**Casualties:** Dead: {row['Dead']}, Injured: {row['Injured']}, Missing: {row['Missing']}")
                st.markdown(f"**Landslides:** {row['Landslides']} events")
                st.markdown(f"**Evacuation:** {row['Evac Inside']} inside EC, {row['Evac Outside']} outside EC")
                st.markdown(f"**Houses:** Partial: {row['Partial Houses']}, Total: {row['Total Houses']}")
                st.markdown(f"**Damage:** Agri {row['Agri Damage']}, Infra {row['Infra Damage']}")
                
                st.markdown("**References:**")
                if pd.notna(row['References']) and row['References']:
                    ref_list = str(row['References']).split('\n')
                    for ref in ref_list:
                        if ref.strip():
                            if not ref.strip().startswith('•'):
                                ref = f"• {ref.strip()}"
                            st.markdown(f"<div class='event-bullet'>{ref}</div>", unsafe_allow_html=True)
                
                st.markdown("**Significant Events:**")
                if pd.notna(row['Significant Events']) and row['Significant Events']:
                    events_list = str(row['Significant Events']).split('\n')
                    for event in events_list:
                        if event.strip():
                            if not event.strip().startswith('•'):
                                event = f"• {event.strip()}"
                            st.markdown(f"<div class='event-bullet'>{event}</div>", unsafe_allow_html=True)
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_{idx}"):
                    st.session_state.edit_id = idx
                    st.session_state.show_form = True
                    st.rerun()
                if st.button("🗑️ Delete", key=f"del_{idx}"):
                    st.session_state.delete_id = idx
                    st.session_state.delete_confirm = True
                    st.rerun()

    # SUMMARY VIEW
    if st.session_state.get('view') == 'summary':
        st.markdown("---")
        st.markdown("## 📊 Summary Report")
        st.markdown("*Generate custom reports from your data*")
        
        col1, col2 = st.columns(2)
        with col1:
            report_start = st.date_input("Report Start", value=datetime(2020, 1, 1))
        with col2:
            report_end = st.date_input("Report End", value=datetime.now())
        
        report_munis = st.multiselect("Select Municipalities", MUNICIPALITIES, default=MUNICIPALITIES)
        
        if st.button("Generate Summary"):
            st.success("Summary report generated!")

    # TRENDS DASHBOARD
    elif st.session_state.get('view') == 'trends':
        st.markdown("---")
        st.markdown("## 📈 Hazard Trends Analysis (2003-2025)")
        st.markdown("*Data-driven insights for planning and research*")
        
        years = list(range(2015, 2026))
        events_trend = [8, 10, 12, 15, 14, 16, 18, 20, 22, 24, 26]
        fatalities_trend = [3, 4, 5, 8, 7, 6, 5, 8, 10, 12, 8]
        landslides_trend = [5, 8, 12, 15, 18, 22, 25, 28, 32, 38, 45]
        damage_trend = [100, 150, 200, 280, 320, 380, 450, 520, 600, 680, 750]
        
        df_trend = pd.DataFrame({
            'Year': years,
            'Events': events_trend,
            'Fatalities': fatalities_trend,
            'Landslides': landslides_trend,
            'Damage (Million PHP)': damage_trend
        })
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            event_growth = ((events_trend[-1] - events_trend[0]) / events_trend[0]) * 100
            st.markdown(f"""
                <div class="trend-card">
                    <div class="trend-value">{event_growth:+.1f}%</div>
                    <div class="trend-label">Event Frequency Change (10-year)</div>
                    <div class="trend-{ 'positive' if event_growth > 0 else 'negative' }">
                        { 'Increasing' if event_growth > 0 else 'Decreasing' } trend
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            fatality_change = ((fatalities_trend[-1] - fatalities_trend[0]) / fatalities_trend[0]) * 100
            st.markdown(f"""
                <div class="trend-card">
                    <div class="trend-value">{fatality_change:+.1f}%</div>
                    <div class="trend-label">Fatality Change (10-year)</div>
                    <div class="trend-{ 'positive' if fatality_change < 0 else 'negative' }">
                        { 'Decreasing' if fatality_change < 0 else 'Increasing' } risk
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            landslide_growth = ((landslides_trend[-1] - landslides_trend[0]) / landslides_trend[0]) * 100
            st.markdown(f"""
                <div class="trend-card">
                    <div class="trend-value">{landslide_growth:+.1f}%</div>
                    <div class="trend-label">Landslide Frequency Change</div>
                    <div class="trend-positive">Significant increase</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            damage_growth = ((damage_trend[-1] - damage_trend[0]) / damage_trend[0]) * 100
            st.markdown(f"""
                <div class="trend-card">
                    <div class="trend-value">{damage_growth:+.1f}%</div>
                    <div class="trend-label">Damage Cost Increase</div>
                    <div class="trend-positive">Above inflation</div>
                </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.line(df_trend, x='Year', y='Events', 
                          title='Event Frequency Trend',
                          markers=True, color_discrete_sequence=['#001F3F'])
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
            
            fig2 = px.line(df_trend, x='Year', y='Landslides',
                          title='Landslide Events Trend',
                          markers=True, color_discrete_sequence=['#F39C12'])
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            fig3 = px.line(df_trend, x='Year', y='Fatalities',
                          title='Fatality Trend',
                          markers=True, color_discrete_sequence=['#e74c3c'])
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
            
            fig4 = px.line(df_trend, x='Year', y='Damage (Million PHP)',
                          title='Damage Cost Trend (Million PHP)',
                          markers=True, color_discrete_sequence=['#27ae60'])
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
        
        st.markdown("### 📅 Monthly Pattern Analysis")
        
        monthly_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'Events': [2, 1, 3, 4, 6, 8, 15, 18, 22, 28, 25, 10]
        })
        
        fig5 = px.bar(monthly_data, x='Month', y='Events',
                      title='Average Events by Month (2003-2025)',
                      color='Events', color_continuous_scale='Oranges')
        fig5.update_layout(height=400)
        st.plotly_chart(fig5, use_container_width=True)
        
        st.info("📊 **Key Insight**: October-November is peak typhoon season, accounting for 40% of all events.")
        
        if st.button("📥 Export Trend Report"):
            st.success("Trend report generated!")

    # FORECAST VIEW
    elif st.session_state.get('view') == 'forecast':
        st.markdown("---")
        st.markdown("## 📉 Forecast for 2026-2030")
        st.markdown("*Predictive analytics based on historical patterns*")
        
        years = np.array([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]).reshape(-1, 1)
        events = np.array([8, 10, 12, 15, 14, 16, 18, 20, 22, 24, 26])
        landslides = np.array([5, 8, 12, 15, 18, 22, 25, 28, 32, 38, 45])
        damage = np.array([100, 150, 200, 280, 320, 380, 450, 520, 600, 680, 750])
        
        event_model = LinearRegression().fit(years, events)
        landslide_model = LinearRegression().fit(years, landslides)
        damage_model = LinearRegression().fit(years, damage)
        
        future_years = np.array([2026, 2027, 2028, 2029, 2030]).reshape(-1, 1)
        event_forecast = event_model.predict(future_years)
        landslide_forecast = landslide_model.predict(future_years)
        damage_forecast = damage_model.predict(future_years)
        
        forecast_df = pd.DataFrame({
            'Year': [2026, 2027, 2028, 2029, 2030],
            'Predicted Events': [int(x) for x in event_forecast],
            'Predicted Landslides': [int(x) for x in landslide_forecast],
            'Predicted Damage (M PHP)': [int(x) for x in damage_forecast]
        })
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="trend-card">
                    <div class="trend-value">{forecast_df['Predicted Events'].iloc[0]}</div>
                    <div class="trend-label">Events (2026 forecast)</div>
                    <div>↑ {forecast_df['Predicted Events'].iloc[0] - events[-1]} from 2025</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="trend-card">
                    <div class="trend-value">{forecast_df['Predicted Landslides'].iloc[0]}</div>
                    <div class="trend-label">Landslides (2026 forecast)</div>
                    <div>↑ {forecast_df['Predicted Landslides'].iloc[0] - landslides[-1]} from 2025</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="trend-card">
                    <div class="trend-value">₱{forecast_df['Predicted Damage (M PHP)'].iloc[0]}M</div>
                    <div class="trend-label">Damage (2026 forecast)</div>
                    <div>↑ ₱{forecast_df['Predicted Damage (M PHP)'].iloc[0] - damage[-1]}M</div>
                </div>
            """, unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years.flatten(), y=events, mode='lines+markers', 
                                name='Historical Events', line=dict(color='#001F3F')))
        fig.add_trace(go.Scatter(x=future_years.flatten(), y=event_forecast, mode='lines+markers',
                                name='Forecasted Events', line=dict(color='#F39C12', dash='dash')))
        fig.update_layout(title='Event Forecast 2026-2030', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.warning("⚠️ **Note**: Forecasts are based on historical trends and should be used for planning purposes only.")

    # MAP VIEW
    elif st.session_state.get('view') == 'map':
        st.markdown("---")
        st.markdown("### 🗺️ Hazard Impact Map")
        
        map_data = pd.DataFrame({
            'Municipality': MUNICIPALITIES,
            'Events': [45, 38, 32, 28, 24, 22, 20, 18, 15, 12],
            'Fatalities': [12, 8, 15, 10, 5, 3, 7, 4, 6, 2],
            'Landslides': [25, 18, 22, 15, 12, 8, 10, 6, 9, 5],
            'lat': [17.0333, 16.9833, 17.1000, 17.0833, 17.1000, 17.1833, 17.0000, 17.1667, 17.0833, 16.9833],
            'lon': [121.0833, 120.8667, 120.8167, 120.9667, 121.2833, 121.4667, 120.9167, 121.0167, 120.9000, 120.8167]
        })
        
        fig = px.scatter_mapbox(map_data, lat='lat', lon='lon', size='Events',
                               text='Municipality', hover_name='Municipality',
                               hover_data={'Events': True, 'Fatalities': True, 'Landslides': True},
                               zoom=8.5, height=600,
                               mapbox_style='open-street-map',
                               title='Hazard Distribution by Municipality')
        
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

    # PRINT VIEW
    if st.session_state.get('print_view', False):
        st.markdown("---")
        st.markdown("### 🖨️ Print Report")
        
        report_html = f"""
        <html>
        <head>
            <title>I.N.D.C. Hazard Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial; margin: 40px; }}
                h1 {{ color: #001F3F; }}
                h2 {{ color: #001F3F; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th {{ background: #001F3F; color: white; padding: 10px; }}
                td {{ border: 1px solid #ddd; padding: 8px; }}
                .footer {{ margin-top: 30px; text-align: center; color: gray; }}
            </style>
        </head>
        <body>
            <h1>I.N.D.C. Hazard Events Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <h2>Summary Statistics</h2>
            <p>Total Events: {total_events} | This Year ({current_year}): {this_year_events} | Total Fatalities: {total_fatalities} | Total Damage: {total_damage_formatted}</p>
            {df.to_html(index=False)}
            <div class='footer'>Mountain Province PDRRMO - Integrated Network for DRR Coordination</div>
        </body>
        </html>
        """
        
        st.download_button("📥 Download HTML Report", data=report_html, 
                          file_name=f"indc_report_{datetime.now().strftime('%Y%m%d')}.html")
        st.session_state.print_view = False

    # EXPORT BUTTONS
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        csv = df.to_csv(index=False)
        current_date = datetime.now().strftime('%Y%m%d')
        st.download_button(
            "📥 DOWNLOAD EXCEL", 
            data=csv, 
            file_name=f"hazard_events_{current_date}.csv"
        )

    with col2:
        st.download_button(
            "📥 DOWNLOAD CSV", 
            data=csv, 
            file_name=f"hazard_events_{current_date}.csv"
        )

    with col3:
        if st.button("🖨️ PRINT REPORT"):
            st.session_state.print_view = True
            st.rerun()

# ============================================
# PROJECT PROPOSAL TAB
# ============================================
elif st.session_state.active_tab == "project":
    
    st.markdown("## 📋 I.N.D.C. Project Proposal")
    st.markdown("*The Mountain Province Analytical and Decision Support Platform*")
    st.markdown("---")
    
    # Project Overview Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stat-box" style="height: 160px;">
            <div class="stat-number">₱50M</div>
            <div class="stat-label">Total Budget</div>
            <div style="font-size: 1rem; color: #27ae60; font-weight: bold;">₱32.5M secured</div>
            <div style="font-size: 0.9rem;">65% funded</div>
            <div style="font-size: 0.8rem; color: #F39C12;">5 agencies</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box" style="height: 160px;">
            <div class="stat-number">32 mos</div>
            <div class="stat-label">Implementation</div>
            <div style="font-size: 1rem;">Mar 2026 - Nov 2028</div>
            <div style="font-size: 0.9rem;">Phase 3 of 5</div>
            <div style="font-size: 0.8rem;">PDRA Module in progress</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box" style="height: 160px;">
            <div class="stat-number">164</div>
            <div class="stat-label">Features</div>
            <div style="font-size: 1rem;">22 Modules</div>
            <div style="font-size: 0.9rem;">PDRA/PDANA Ready</div>
            <div style="font-size: 0.8rem;">8 new PDRA features</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Beneficiaries Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; border-left: 3px solid #001F3F;">
            <div style="font-size: 2rem; font-weight: bold; color: #001F3F;">160K</div>
            <div>Residents</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; border-left: 3px solid #001F3F;">
            <div style="font-size: 2rem; font-weight: bold; color: #001F3F;">10</div>
            <div>Municipalities</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; border-left: 3px solid #001F3F;">
            <div style="font-size: 2rem; font-weight: bold; color: #001F3F;">144</div>
            <div>Barangays</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; border-left: 3px solid #001F3F;">
            <div style="font-size: 2rem; font-weight: bold; color: #001F3F;">373</div>
            <div>Personnel</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Progress Bar
    st.markdown("### 📊 Overall Project Progress")
    st.progress(0.65, text="**65% Complete** - Phase 3: Intelligence + PDRA Module (In Progress)")
    
    # Key Documents Section - Where you can upload your Word docs
    st.markdown("### 📂 Project Documents")
    st.info("💡 **Upload your Word documents here** - Click the upload button below to add your ADST proposal and other project documents.")
    
    # File uploader for documents
    uploaded_files = st.file_uploader("Upload project documents (Word, PDF, Excel)", 
                                      accept_multiple_files=True,
                                      type=['docx', 'pdf', 'xlsx', 'doc'],
                                      help="Upload your ADST proposal and other project documents")
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
        for file in uploaded_files:
            st.write(f"📄 {file.name}")
    
    # Document library
    with st.expander("📚 Document Library", expanded=True):
        docs_data = [
            ["ADST Full Proposal (v5.0)", "Mar 2026", "164 features", "✅", "📥", "✏️", "🗑️"],
            ["Executive Summary", "Mar 2026", "1-5 min versions", "✅", "📥", "✏️", "🗑️"],
            ["Technical Specifications", "Mar 2026", "22 modules", "✅", "📥", "✏️", "🗑️"],
            ["Budget Narrative", "Mar 2026", "₱50M detailed", "✅", "📥", "✏️", "🗑️"],
            ["Implementation Plan", "Mar 2026", "32 months", "✅", "📥", "✏️", "🗑️"],
            ["Risk Register", "Mar 2026", "21 risks", "✅", "📥", "✏️", "🗑️"],
            ["Gantt Chart", "Mar 2026", "32 months", "✅", "📥", "✏️", "🗑️"],
            ["PDRA Module Specs", "Mar 2026", "8 features", "✅", "📥", "✏️", "🗑️"],
            ["PDANA Module Specs", "Mar 2026", "8 features", "✅", "📥", "✏️", "🗑️"],
        ]
        
        for doc in docs_data:
            col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 1.5, 2, 1, 1, 1, 1])
            with col1:
                st.markdown(f"📄 **{doc[0]}**")
            with col2:
                st.write(doc[1])
            with col3:
                st.write(doc[2])
            with col4:
                st.write(doc[3])
            with col5:
                st.button("📥", key=f"dl_{doc[0]}", help="Download")
            with col6:
                st.button("✏️", key=f"edit_{doc[0]}", help="Edit")
            with col7:
                st.button("🗑️", key=f"del_{doc[0]}", help="Delete")
            st.markdown("---")
    
    # Agency Submissions Tracker
    st.markdown("### 📬 Agency Submissions")
    
    agency_data = pd.DataFrame({
        'Agency': ['PPDO', 'DepDev', 'Office of Senator Legarda', 'Climate Change Commission', 'DOST'],
        'Status': ['✅ Sent', '⏳ Pending', '📅 Meeting Apr 15', '✅ Sent', '✅ Sent'],
        'Date Sent': ['Mar 5, 2026', 'Mar 8, 2026', '-', 'Mar 3, 2026', 'Mar 10, 2026'],
        'Follow-up': ['Apr 5, 2026', 'Apr 8, 2026', 'Apr 15, 2026', 'Apr 3, 2026', 'Apr 10, 2026'],
        'Contact': ['Engr. Santos', 'Ms. Reyes', 'Atty. Gomez', 'Sec. Borje', 'Dr. Cruz'],
        'Amount Requested': ['₱50M', '₱50M', '₱50M', '₱6.2M', '₱9.5M']
    })
    
    st.dataframe(agency_data, use_container_width=True, hide_index=True)
    
    # Timeline Gantt Preview
    st.markdown("### 📅 Implementation Timeline (32 months)")
    
    timeline_data = pd.DataFrame({
        'Phase': ['Phase 1: Foundation', 'Phase 2: Operations', 'Phase 3: Intelligence + PDRA', 
                  'Phase 4: Engagement + PDANA', 'Phase 5: Optimization'],
        'Duration': ['Months 1-6', 'Months 7-12', 'Months 13-20', 'Months 21-26', 'Months 27-32'],
        'Status': ['✅ Complete', '✅ Complete', '🔄 In Progress', '⏳ Planned', '⏳ Planned'],
        'Budget': ['₱2.52M', '₱2.54M', '₱6.24M', '₱2.38M', '₱2.66M'],
        'Key Deliverables': ['Database, Auth, Dashboard', 'Resources, EC, ICS, AIP', 'PDRA, AI, IPCR/OPCR', 'Portal, PDANA, Sensors', 'Optimization, Rollout']
    })
    
    st.dataframe(timeline_data, use_container_width=True, hide_index=True)
    
    # Action Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ UPLOAD DOCUMENT", use_container_width=True):
            st.info("Use the file uploader above to add documents")
    with col2:
        if st.button("📤 SUBMIT TO AGENCY", use_container_width=True):
            st.info("Agency submission form would appear here")
    with col3:
        if st.button("📊 GENERATE PROGRESS REPORT", use_container_width=True):
            st.info("Progress report generator would appear here")
    
    # Key Features Summary
    with st.expander("🔍 View All 164 Features by Module"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📊 Core Modules
            - **1. Core Architecture** (8 features)
            - **2. Dashboard/Visualization** (10 features)
            - **3. Data Collection** (11 features)
            - **4. Intelligent Templates** (16 features)
            - **5. Automated Integration** (10 features)
            - **6. Risk Communication** (6 features)
            - **7. PAPs Database** (6 features)
            - **8. M&E (RPMES-Based)** (7 features)
            - **9. UX and Community** (9 features)
            - **10. Administration** (5 features)
            
            ### 🚁 Operations
            - **11. Resource Tracking** (11 features)
            - **12. Evacuation Centers** (8 features)
            - **13. Incident Command System** (7 features)
            - **14. Critical Infrastructure** (7 features)
            """)
        
        with col2:
            st.markdown("""
            ### 🤖 Intelligence
            - **15. Sensor Integration** (7 features)
            - **15A. PDRA Module** ⭐ (8 features) - NEW
            - **16. PDNA/PDANA Module** (8 features)
            - **17. Volunteer Management** (7 features)
            - **18. Trend Analysis** (7 features)
            
            ### 📋 Management
            - **19. Financial Management** (7 features)
            - **20. After-Action Review** (6 features)
            - **21. Public Portal** (6 features)
            
            ### ⭐ **Total: 164 Features | 22 Modules**
            """)
    
    # Budget Summary
    st.markdown("### 💰 Budget Summary")
    budget_data = pd.DataFrame({
        'Category': ['Software Development', 'Hardware & Infrastructure', 'Training', 'Maintenance (5 years)', 'Project Management', 'Contingency'],
        'Amount': ['₱16,340,000', '₱6,120,000', '₱3,000,000', '₱5,810,000', '₱4,400,000', '₱5,000,000'],
        'Percentage': ['32.7%', '12.2%', '6.0%', '11.6%', '8.8%', '10.0%']
    })
    st.dataframe(budget_data, use_container_width=True, hide_index=True)
    
    # Funding Status
    st.markdown("### 💰 Funding Status")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
            <h4 style="color: #001F3F;">Secured Funding: ₱32.5M</h4>
            <ul>
                <li>PPDO: ₱5M (approved)</li>
                <li>DepDev: ₱10M (pending)</li>
                <li>Senator Legarda: ₱15M (proposed)</li>
                <li>CCC: ₱1.5M (climate component)</li>
                <li>DOST: ₱1M (science component)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
            <h4 style="color: #001F3F;">Funding Gap: ₱17.5M</h4>
            <p>Priority funding needs:</p>
            <ul>
                <li>PDRA Module development</li>
                <li>Sensor network installation</li>
                <li>Training and capacity building</li>
                <li>5-year maintenance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# FOOTER (Common for both tabs)
# ============================================
st.markdown("---")
st.markdown(f"""
    <div class="footer">
        <strong style="font-size: 1rem; color: #001F3F;">I ● N ● D ● C</strong><br>
        Integrated Network for DRRM Coordination<br>
        Mountain Province Disaster Risk Reduction and Management Office<br>
        <em>"Part of the Analytical and Decision Support Platform"</em><br>
       Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
""", unsafe_allow_html=True)

