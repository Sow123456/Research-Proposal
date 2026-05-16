import streamlit as st
import os
import io
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# --- PAGE CONFIG ---
st.set_page_config(page_title="ProGen: Global Grant Resource Hub", page_icon="🌐", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #2563eb; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1d4ed8; }
    .portal-card { padding: 20px; border: 1px solid #e2e8f0; background-color: #ffffff; margin-bottom: 15px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .link-btn { display: inline-block; padding: 10px 20px; background-color: #2563eb; color: white !important; text-decoration: none; border-radius: 6px; font-weight: 600; margin-top: 10px; transition: 0.3s; }
    .link-btn:hover { background-color: #1e40af; }
    .secondary-link { display: inline-block; padding: 8px 15px; background-color: #f1f5f9; color: #1e293b !important; text-decoration: none; border-radius: 6px; font-weight: 500; margin-top: 10px; margin-left: 10px; border: 1px solid #cbd5e1; }
    .agency-header { color: #1e3a8a; border-bottom: 2px solid #2563eb; padding-bottom: 5px; margin-bottom: 15px; }
    .tag { padding: 4px 8px; border-radius: 4px; background: #f0fdf4; color: #166534; font-size: 11px; font-weight: bold; margin-right: 5px; margin-bottom: 5px; display: inline-block; border: 1px solid #dcfce7; }
    </style>
    """, unsafe_allow_html=True)

# --- HYPER-SENSITIVE AGENCY DATABASE ---
# Expanded tags to catch niche topics like EEG, Signal Processing, AI classification
AGENCY_DATA = {
    "ICMR (Medical & Health)": {
        "portal": "https://epms.icmr.org.in/",
        "guidelines": "https://icmr.gov.in/information-rules-manuals",
        "focus": "Biomedical research, clinical trials, neurology, and health AI.",
        "tags": ["medical", "health", "eeg", "brain", "clinical", "neurology", "signal", "classification", "patient", "biomedical", "ai", "machine learning"]
    },
    "SERB / ANRF (Science & Engineering)": {
        "portal": "https://www.anrfonline.in/",
        "guidelines": "https://dst.gov.in/anusandhan-national-research-foundation-anrf",
        "focus": "Core research in all areas of Science, Engineering, and Math.",
        "tags": ["science", "engineering", "math", "physics", "ai", "eeg", "signal", "algorithm", "innovation", "fundamental", "computation"]
    },
    "MeitY (Electronics & IT)": {
        "portal": "https://www.meity.gov.in/content/research-development",
        "guidelines": "https://www.meity.gov.in/content/schemes-and-projects",
        "focus": "IT, Electronics, AI/ML, and Cyber Security.",
        "tags": ["it", "electronics", "ai", "machine learning", "ml", "classification", "digital", "software", "computation", "algorithm"]
    },
    "DST (Tech Development)": {
        "portal": "https://onlinedst.gov.in/",
        "guidelines": "https://dst.gov.in/call-for-proposals",
        "focus": "Technology commercialization, prototypes, and devices.",
        "tags": ["technology", "prototype", "device", "innovation", "product", "commercial", "hardware"]
    },
    "BIRAC (Biotech Industry)": {
        "portal": "https://birac.nic.in/login.php",
        "guidelines": "https://birac.nic.in/desc_new.php?id=77",
        "focus": "Biotech startups, product development, and industry link.",
        "tags": ["biotech", "startup", "innovation", "biology", "genetics", "agriculture", "pharma", "medical device"]
    },
    "DRDO (Defence Research)": {
        "portal": "https://www.drdo.gov.in/extramural-research",
        "guidelines": "https://www.drdo.gov.in/forms-and-manuals",
        "focus": "Defence, Electronics, Aeronautics, and Security.",
        "tags": ["defence", "security", "electronics", "signal", "radar", "robotics", "drone", "aerospace"]
    },
    "DBT (Biotechnology)": {
        "portal": "https://dbtepromis.nic.in/",
        "guidelines": "https://dst.gov.in/call-for-proposals",
        "focus": "Agriculture, Health, and Environmental Biotechnology.",
        "tags": ["biotech", "genetics", "biology", "agriculture", "environment", "health"]
    },
    "CSIR (Industrial R&D)": {
        "portal": "https://www.csir.res.in/",
        "guidelines": "https://www.csir.res.in/career-opportunities/grants-fellowships",
        "focus": "Broad industrial research and multi-disciplinary science.",
        "tags": ["industrial", "science", "chemical", "nanotech", "geophysics", "applied"]
    },
    "MSME (Innovation)": {
        "portal": "https://my.msme.gov.in/inc/",
        "guidelines": "https://innovative.msme.gov.in/",
        "focus": "Small enterprise innovation and startups.",
        "tags": ["startup", "business", "innovation", "msme", "design"]
    },
    "ISRO (Space Research)": {
        "portal": "https://www.isro.gov.in/capacity-building/respond-projects",
        "guidelines": "https://www.isro.gov.in/RESPOND.html",
        "focus": "Space science, satellite tech, and atmospheric research.",
        "tags": ["space", "satellite", "astronomy", "physics", "remote sensing"]
    },
    "C-DAC (Advanced Computing)": {
        "portal": "https://www.cdac.in/",
        "guidelines": "https://www.cdac.in/index.aspx?id=R_D_projects",
        "focus": "Supercomputing and advanced IT R&D.",
        "tags": ["computing", "supercomputer", "ai", "network", "software"]
    },
    "MNRE (Renewable Energy)": {
        "portal": "https://mnre.gov.in/",
        "guidelines": "https://mnre.gov.in/knowledge-center/r-and-d-proposals",
        "focus": "Solar, Wind, and Green Energy.",
        "tags": ["solar", "wind", "energy", "renewable", "green"]
    },
    "MoFPI (Food Processing)": {
        "portal": "https://www.mofpi.gov.in/",
        "guidelines": "https://www.mofpi.gov.in/Schemes/research-development",
        "focus": "Food technology and nutrition.",
        "tags": ["food", "agriculture", "processing", "nutrition"]
    },
    "ICSSR (Social Science)": {
        "portal": "https://icssr.org/grants",
        "guidelines": "https://icssr.org/research-projects",
        "focus": "Social, economic, and policy research.",
        "tags": ["social", "psychology", "economics", "humanities", "policy"]
    }
}

# --- PDF GENERATOR ---
def create_portal_report(idea, selected_agencies):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(30, 58, 138)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(15)
    pdf.cell(0, 10, 'MASTER GRANT DISCOVERY DIRECTORY', align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(50)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, "Target Research Concept: " + idea[:60] + "...", ln=True)
    pdf.ln(5)
    for name in selected_agencies:
        data = AGENCY_DATA.get(name, {})
        pdf.set_fill_color(240, 247, 255)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 10, f" AGENCY: {name}", ln=True, fill=True)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 7, f"Portal: {data.get('portal')}\nOfficial Guidelines: {data.get('guidelines')}\nFocus: {data.get('focus')}")
        pdf.ln(5)
    return bytes(pdf.output())

# --- UI MAIN ---
st.title("🏦 ProGen: Hyper-Sensitive Grant Discovery")
st.markdown("Scanning all agencies with **Ultra-Sensitivity**. Surfacing every portal with even a minor relevance.")

idea_input = st.text_area("Your Research Idea (e.g., AI for EEG classification)", placeholder="Type here...", height=100)

if st.button("🚀 Deep Scan (High Sensitivity)"):
    if not idea_input:
        st.warning("Please enter your idea.")
    else:
        results = []
        idea_l = idea_input.lower()
        
        # Hyper-Sensitive Matching
        for name, data in AGENCY_DATA.items():
            # Match if ANY tag is in the idea, or ANY word of the idea is in the tags
            # Also match if the focus contains any key tech words from the idea
            match_found = False
            for tag in data['tags']:
                if tag in idea_l: match_found = True; break
            
            if not match_found:
                # Secondary check: broad domain match
                if "ai" in idea_l or "classification" in idea_l or "machine learning" in idea_l:
                    if "ai" in data['tags'] or "computation" in data['tags']: match_found = True
            
            if match_found:
                results.append(name)
        
        # Always include DST and SERB/ANRF as they are universal funders for Tech/Science
        results.append("SERB / ANRF (Science & Engineering)")
        results.append("DST (Tech Development)")
        
        st.session_state.matched_portals = list(set(results))
        st.success(f"🎯 High-Sensitivity Scan Complete: Found {len(st.session_state.portals if 'portals' in st.session_state else st.session_state.matched_portals)} portals!")

if "matched_portals" in st.session_state:
    st.subheader("🏦 All Potentially Relevant Portals")
    for name in st.session_state.matched_portals:
        data = AGENCY_DATA.get(name, {})
        with st.container():
            st.markdown(f"""
            <div class="portal-card">
                <h3 class="agency-header">{name}</h3>
                <div style="margin-bottom: 10px;">
                    {" ".join([f'<span class="tag">#{tag}</span>' for tag in data['tags']])}
                </div>
                <p><strong>Focus:</strong> {data['focus']}</p>
                <div style="margin-top: 15px;">
                    <a href="{data['portal']}" target="_blank" class="link-btn">🔗 Open Portal</a>
                    <a href="{data['guidelines']}" target="_blank" class="secondary-link">📖 Guidelines & Budget</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    if st.button("📕 Export All Matches (PDF)"):
        pdf_bytes = create_portal_report(idea_input, st.session_state.matched_portals)
        st.download_button("💾 Download Directory", data=pdf_bytes, file_name="Grant_Discovery_Report.pdf", mime="application/pdf")
