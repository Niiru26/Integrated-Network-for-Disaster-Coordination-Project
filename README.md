# 🌊 I.N.D.C. - Integrated Network for DRRM Coordination

### Mountain Province Disaster Risk Reduction and Management Office Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://integrated-network-for-disaster-coordination-project-ey6zq6u3w.streamlit.app/)

---

## 📋 Overview

The **Integrated Network for DRRM Coordination (I.N.D.C.)** is a comprehensive disaster risk reduction management platform built for the Mountain Province Disaster Risk Reduction & Management Office. It transforms 20+ years of hydrometeorological hazard data into actionable intelligence through interactive dashboards, trend analysis, and predictive forecasting.

---

## ✨ Key Features

### 📊 **1. Hazard Events Database**
- Track typhoons, super typhoons, tropical storms, monsoons, LPAs, ITCZ, and shear lines
- Record casualties (dead, injured, missing)
- Document damaged houses (partial and total)
- Track displacement data (inside/outside evacuation centers)
- Log landslide events and road closures
- Store references and official issuances

### 📈 **2. Trend Analysis Dashboard**
- 10-year trend analysis for event frequency
- Fatality trends and patterns
- Landslide frequency tracking
- Damage cost trends
- Monthly pattern analysis (identifies October-November as peak season)
- Year-over-year comparisons

### 🔮 **3. Predictive Forecasting**
- Machine learning-based forecasts for 2026-2030
- Predicted events, landslides, and damage costs
- Historical pattern recognition using scikit-learn

### 🗺️ **4. Interactive Map View**
- Geographic visualization of hazards by municipality
- Size-coded markers based on event frequency
- Hover details for fatalities and landslides
- OpenStreetMap integration

### 📝 **5. Smart Data Entry**
- Step-by-step form with validation
- ALL CAPS enforcement for typhoon names
- Auto-bulleting for references and significant events
- Real-time input validation
- Quick guide for significant events

### 📥 **6. Export & Reporting**
- Download data as Excel/CSV
- Generate HTML reports (printable as PDF)
- Summary statistics dashboard
- 6 key metrics at a glance (Events, Fatalities, Landslides, Evacuees, Agri Damage, Infra Damage)

---

## 🏛️ Municipalities Covered

| | | | | |
|---|---|---|---|---|
| Barlig | Bauko | Besao | Bontoc | Natonin |
| Paracelis | Sabangan | Sadanga | Sagada | Tadian |

---

## 📊 Key Statistics Tracked

| Metric | Cumulative | Current Year |
|--------|------------|--------------|
| Events | ✅ | ✅ |
| Fatalities | ✅ | ✅ |
| Landslides | ✅ | ✅ |
| Evacuees | ✅ | ✅ |
| Agriculture Damage | ✅ | ✅ |
| Infrastructure Damage | ✅ | ✅ |

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Database | Supabase (PostgreSQL) |
| Charts | Plotly |
| Machine Learning | scikit-learn |
| Data Processing | Pandas, NumPy |
| Deployment | Streamlit Community Cloud |

---

## 🚀 Live Demo

Access the application here:
👉 **[I.N.D.C. Live App](https://integrated-network-for-disaster-coordination-project-ey6zq6u3w.streamlit.app/)**

---

## 📁 Project Structure
📦 Integrated Network for Disaster Risk Reduction & Management Coordination Project
├── 📄 indc_app.py # Main application
├── 📄 requirements.txt # Python dependencies
├── 📄 logo.png # PDRRMO logo
├── 📁 01_Scripts/ # Utility scripts
├── 📁 02_Data/ # Data files
├── 📁 03_Backups/ # Database backups
├── 📁 04_Documentation/ # Documentation
└── 📁 05_Exports/ # Exported reports
---

## 💻 Local Development

To run this app locally:

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/indc-app.git
   cd indc-app
   pip install -r requirements.txt
   streamlit run indc_app.py
   📝 Data Entry Guide
For Significant Events, include:
✅ PDRA conduct dates

✅ TCWS hoisting dates and levels

✅ Alert level changes

✅ Road closures (specific locations)

✅ Power interruptions

✅ Communication issues

✅ Evacuation numbers

✅ Landslide counts

✅ Class suspensions

✅ State of calamity declarations

🔒 Security
Database credentials stored as Streamlit secrets

No sensitive data exposed in code

Supabase provides secure cloud database

👥 Intended Users
PDRRMO personnel

Municipal DRRM officers

Disaster response planners

Researchers and analysts

Provincial government officials

🎯 Future Enhancements
User authentication system

Mobile app version for field reporting

Automated PAGASA/PHIVOLCS integration

Real-time weather data feeds

SMS alert system

Resource tracking module

Evacuation center management

📞 Contact
Mountain Province PDRRMO

Office: Ian Neil D. Culallad

Email: cneil_japan@yahoo.com.ph
🙏 Acknowledgments
Built with Streamlit, powered by Mountain Province's 20+ years of disaster data, and a vision for data-driven DRRM.

"Transforming data into decisions, fragmentation into coordination, and reaction into readiness."

© 2026 I.N.D.C. - Integrated Network for DRRM Coordination

## 📝 How to Add This to GitHub

1. **Go to** your GitHub repository
2. **Click** on `README.md` (or create it if it doesn't exist)
3. **Click** the pencil icon (✏️) to edit
4. **Delete** any existing content
5. **Copy and paste** the entire markdown above
6. **Replace** `YOUR-USERNAME` with your actual GitHub username
7. **Add** your contact information
8. **Scroll down** and click **"Commit changes"**

## ✅ This README now includes:

- Professional project description
- Complete feature list
- Technology stack
- Live demo link
- Project structure
- Local development instructions
- Data entry guide
- Future roadmap
- Contact information

Your GitHub repository will look **professional and comprehensive**! 🚀
