import streamlit as st
import pandas as pd
import time
from datetime import datetime
from sqlalchemy import text
from streamlit_option_menu import option_menu

# --- Constants & Config ---
st.set_page_config(
    page_title="Creatio-Style CRM",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to mimic Creatio's styling
st.markdown("""
<style>
    .metric-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: white;
        color: black;
    }
    .metric-title {
        font-size: 14px;
        color: #555;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .metric-value-green {
        font-size: 36px;
        color: #28a745; /* Creatio Green */
        font-weight: 700;
    }
    .metric-value-blue {
        font-size: 36px;
        color: #007bff; /* Creatio Blue */
        font-weight: 700;
    }
    /* Hide Streamlit default padding for top */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

STAGES = ["New", "Contacted", "Qualified", "Closed"]

# --- Database Connection ---
conn = st.connection('sql', type='sql', url='sqlite:///crm_database.db')

def init_db():
    with conn.session as s:
        s.execute(text('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                company TEXT,
                lead_source TEXT,
                stage TEXT,
                created_at TIMESTAMP
            )
        '''))
        s.execute(text('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                activity_type TEXT,
                details TEXT,
                created_at TIMESTAMP
            )
        '''))
        s.commit()

init_db()

# --- Helper Functions ---
def add_lead(first_name, last_name, email, company, lead_source):
    created_at = datetime.now()
    with conn.session as s:
        s.execute(text('''
            INSERT INTO leads (first_name, last_name, email, company, lead_source, stage, created_at)
            VALUES (:fn, :ln, :em, :co, :ls, :st, :ca)
        '''), {'fn': first_name, 'ln': last_name, 'em': email, 'co': company, 'ls': lead_source, 'st': 'New', 'ca': created_at})
        s.commit()
        result = s.execute(text("SELECT id FROM leads ORDER BY id DESC LIMIT 1")).fetchone()
        lead_id = result[0]
        s.execute(text('''
            INSERT INTO activities (lead_id, activity_type, details, created_at)
            VALUES (:lid, :at, :det, :ca)
        '''), {'lid': lead_id, 'at': 'System', 'det': 'Lead created via Dashboard.', 'ca': created_at})
        s.commit()
    return lead_id

def update_lead_stage(lead_id, new_stage):
    with conn.session as s:
        s.execute(text("UPDATE leads SET stage = :ns WHERE id = :id"), {'ns': new_stage, 'id': lead_id})
        s.execute(text('''
            INSERT INTO activities (lead_id, activity_type, details, created_at)
            VALUES (:lid, :at, :det, :ca)
        '''), {'lid': lead_id, 'at': 'Stage Change', 'det': f'Moved to {new_stage}', 'ca': datetime.now()})
        s.commit()

def log_activity(lead_id, activity_type, details):
    with conn.session as s:
        s.execute(text('''
            INSERT INTO activities (lead_id, activity_type, details, created_at)
            VALUES (:lid, :at, :det, :ca)
        '''), {'lid': lead_id, 'at': activity_type, 'det': details, 'ca': datetime.now()})
        s.commit()

def get_leads_df():
    return conn.query("SELECT * FROM leads ORDER BY created_at DESC")

def get_activities_df():
    return conn.query("SELECT * FROM activities ORDER BY created_at DESC")

def mock_ai_generate_email(first_name, company, source):
    time.sleep(1.5)
    hook = f"I noticed you requested more information on our website." if source == 'Website' else f"It was great meeting you at the recent conference!" if source == 'Conference' else f"I wanted to reach out regarding your interest in our platform."
    draft = f"Hi {first_name},\n\n{hook} We specialize in helping companies like {company} streamline their workflows.\n\nDo you have 10 minutes next week for a quick demo? Book here: https://calendly.com/demo\n\nBest,\nSales Team"
    return "Demo Request Follow-up", draft

leads_df = get_leads_df()
activities_df = get_activities_df()

# --- SIDEBAR NAVIGATION (Creatio Style) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png", width=50) # Placeholder Logo
    
    selected_menu = option_menu(
        menu_title="All apps",
        options=["Home", "Contacts", "Campaigns", "Email", "Landing pages", "Events", "Leads", "Accounts", "Dashboards", "Marketing plans"],
        icons=["house", "person-badge", "megaphone", "envelope", "window", "balloon", "person-lines-fill", "building", "bar-chart", "calendar"],
        menu_icon="cast",
        default_index=2, # Default to Campaigns
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#a0a0a0", "font-size": "18px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#333"},
            "nav-link-selected": {"background-color": "#444"},
        }
    )

# --- MAIN LAYOUT ---
if selected_menu == "Campaigns":
    
    st.markdown("### ← Creatio 'No-code days Miami' event invitation & products promotion campaign")
    
    # Define Layout Columns matching Creatio
    col_left, col_right = st.columns([1, 3])
    
    # --- LEFT COLUMN (KPIs & Info) ---
    with col_left:
        with st.expander("Campaign info", expanded=True):
            st.markdown("**Name\\***\nCapturing audience for webinar: «marketing: several approaches on how to nurture your customer's leads»")
            st.caption("Goal")
            
            # Custom KPI Cards matching screenshot
            closed_deals = len(leads_df[leads_df['stage'] == 'Closed']) if not leads_df.empty else 0
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Reached the goal</div>
                    <div class="metric-value-green">{closed_deals}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Participants (Total Leads)</div>
                    <div class="metric-value-blue">{len(leads_df)}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with st.expander("Workflow settings", expanded=True):
            st.markdown("**Start mode**\nAt the specified time")
            st.markdown("**Start time**\n8/3/2026 2:51 PM")
            st.markdown("**Stop mode**\nAt the specified time")
            
    # --- RIGHT COLUMN (Main Workspace Tabs) ---
    with col_right:
        tab_flow, tab_audience, tab_linked, tab_add = st.tabs(["CAMPAIGN FLOW (Pipeline)", "AUDIENCE (Database)", "LINKED ENTITY", "➕ ADD PARTICIPANT"])
        
        with tab_flow:
            if leads_df.empty:
                st.info("No leads in the pipeline. Click the '➕ ADD PARTICIPANT' tab to get started!")
            else:
                stage_cols = st.columns(len(STAGES))
                for i, stage in enumerate(STAGES):
                    with stage_cols[i]:
                        st.markdown(f"**{stage}**")
                        stage_leads = leads_df[leads_df['stage'] == stage]
                        for _, lead in stage_leads.iterrows():
                            with st.container(border=True):
                                st.markdown(f"**{lead['first_name']} {lead['last_name']}**")
                                st.caption(f"{lead['company']} ({lead['lead_source']})")
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if i > 0 and st.button("⬅️", key=f"prev_{lead['id']}"):
                                        update_lead_stage(lead['id'], STAGES[i-1])
                                        st.rerun()
                                with col_b:
                                    if i < len(STAGES) - 1 and st.button("➡️", key=f"next_{lead['id']}"):
                                        update_lead_stage(lead['id'], STAGES[i+1])
                                        st.rerun()
                                
                                with st.expander("AI Email"):
                                    if st.button("Generate Draft", key=f"ai_{lead['id']}"):
                                        with st.spinner("AI drafting..."):
                                            subj, body = mock_ai_generate_email(lead['first_name'], lead['company'], lead['lead_source'])
                                            st.session_state[f"draft_subj_{lead['id']}"] = subj
                                            st.session_state[f"draft_body_{lead['id']}"] = body
                                    
                                    if f"draft_subj_{lead['id']}" in st.session_state:
                                        st.text_input("Subject", value=st.session_state[f"draft_subj_{lead['id']}"], key=f"input_subj_{lead['id']}")
                                        st.text_area("Body", value=st.session_state[f"draft_body_{lead['id']}"], height=200, key=f"input_body_{lead['id']}")
                                        if st.button("Send Email", key=f"send_{lead['id']}"):
                                            log_activity(lead['id'], "Email", f"Sent: {st.session_state[f'draft_subj_{lead['id']}']}")
                                            st.success("Sent!")
                                            st.rerun()

        with tab_audience:
            if not leads_df.empty:
                st.dataframe(leads_df, hide_index=True, use_container_width=True)
                st.markdown("### Global Activity Log")
                st.dataframe(activities_df, hide_index=True, use_container_width=True)
            else:
                st.info("Database is empty. Click the '➕ ADD PARTICIPANT' tab to get started!")
                
        with tab_linked:
            st.info("Linked Entities configuration goes here.")
            
        with tab_add:
            with st.form("lead_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name")
                    email = st.text_input("Email Address")
                    lead_source = st.selectbox("Lead Source", ["Website", "Referral", "Conference", "Cold Call", "Other"])
                with col2:
                    last_name = st.text_input("Last Name")
                    company = st.text_input("Company")
                
                if st.form_submit_button("Save Participant", type="primary"):
                    if not first_name or not email:
                        st.error("First Name and Email are required.")
                    else:
                        add_lead(first_name, last_name, email, company, lead_source)
                        st.success("Participant added successfully!")
                        time.sleep(1)
                        st.rerun()
else:
    st.title(selected_menu)
    st.info(f"The {selected_menu} module is under construction.")
