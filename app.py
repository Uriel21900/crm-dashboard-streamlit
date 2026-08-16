import streamlit as st
import pandas as pd
import time
from datetime import datetime
import json
from sqlalchemy import text

# --- Constants & Config ---
st.set_page_config(
    page_title="CRM Dashboard 2.0",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

STAGES = ["New", "Contacted", "Qualified", "Closed"]

# --- Database Connection (Cloud-Ready) ---
# By using st.connection('sql'), migrating to Postgres is just changing the secrets.toml URL!
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
        
        # Get the inserted ID
        result = s.execute(text("SELECT id FROM leads ORDER BY id DESC LIMIT 1")).fetchone()
        lead_id = result[0]
        
        # Log creation activity
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

def get_activities_df(lead_id=None):
    if lead_id:
        return conn.query(f"SELECT * FROM activities WHERE lead_id = {lead_id} ORDER BY created_at DESC")
    return conn.query("SELECT * FROM activities ORDER BY created_at DESC")

def mock_ai_generate_email(first_name, company, source):
    """Mocks calling an LLM (like Ollama or Gemini) to generate an email draft"""
    time.sleep(1.5) # Simulate API latency
    if source == 'Conference':
        hook = f"It was great meeting you at the recent conference!"
    elif source == 'Website':
        hook = f"I noticed you requested more information on our website."
    else:
        hook = f"I wanted to reach out regarding your interest in our platform."
        
    draft = f"""Hi {first_name},

{hook} We specialize in helping companies like {company} streamline their workflows and boost productivity. 

I would love to show you how we can help. Do you have 10 minutes next week for a quick demo? You can book a time directly on my calendar here: https://calendly.com/demo

Best regards,

Sales Team
Acme Corp
sales@acmecorp.com"""
    return "Demo Request Follow-up", draft

# --- UI Layout ---
st.title("💼 Modern CRM Dashboard")

leads_df = get_leads_df()
activities_df = get_activities_df()

# 1. High Level KPIs (Inverted Pyramid Top)
st.markdown("### Executive Summary")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Leads", len(leads_df))
with col2:
    closed_leads = len(leads_df[leads_df['stage'] == 'Closed']) if not leads_df.empty else 0
    st.metric("Closed Deals", closed_leads)
with col3:
    conversion_rate = f"{(closed_leads / len(leads_df) * 100):.1f}%" if not leads_df.empty and len(leads_df) > 0 else "0%"
    st.metric("Conversion Rate", conversion_rate)
with col4:
    emails_sent = len(activities_df[activities_df['activity_type'] == 'Email']) if not activities_df.empty else 0
    st.metric("Emails Sent", emails_sent)

st.divider()

# 2. Tabs for Workflow
tab_pipeline, tab_db, tab_add_lead = st.tabs(["🚀 Lead Pipeline (Kanban)", "📋 Database & Activity", "➕ Add New Lead"])

# --- TAB 1: Lead Pipeline (Kanban) ---
with tab_pipeline:
    st.markdown("### Active Pipeline")
    if leads_df.empty:
        st.info("No leads in the pipeline. Add a lead to get started.")
    else:
        # Create columns for each stage
        stage_cols = st.columns(len(STAGES))
        
        for i, stage in enumerate(STAGES):
            with stage_cols[i]:
                st.markdown(f"**{stage}**")
                stage_leads = leads_df[leads_df['stage'] == stage]
                
                for _, lead in stage_leads.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{lead['first_name']} {lead['last_name']}**")
                        st.caption(f"{lead['company']} ({lead['lead_source']})")
                        
                        # Navigation buttons for the pipeline
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if i > 0:
                                if st.button("⬅️", key=f"prev_{lead['id']}", help="Move back"):
                                    update_lead_stage(lead['id'], STAGES[i-1])
                                    st.rerun()
                        with col_b:
                            if i < len(STAGES) - 1:
                                if st.button("➡️", key=f"next_{lead['id']}", help="Move forward"):
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


# --- TAB 2: Database & Activity ---
with tab_db:
    st.markdown("### CRM Database")
    if not leads_df.empty:
        st.dataframe(
            leads_df,
            column_config={
                "id": "ID",
                "first_name": "First Name",
                "last_name": "Last Name",
                "email": "Email",
                "company": "Company",
                "lead_source": "Source",
                "stage": "Pipeline Stage",
                "created_at": st.column_config.DatetimeColumn("Date Added", format="D MMM YYYY, h:mm a"),
            },
            hide_index=True,
            use_container_width=True
        )
        csv = leads_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data as CSV", data=csv, file_name='crm_leads.csv', mime='text/csv')
        
        st.divider()
        st.markdown("### Global Activity Log")
        st.dataframe(activities_df, hide_index=True, use_container_width=True)
    else:
        st.info("Database is empty.")


# --- TAB 3: Add New Lead ---
with tab_add_lead:
    st.markdown("### Enter Lead Information")
    with st.form("lead_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", placeholder="Jane")
            email = st.text_input("Email Address", placeholder="jane@company.com")
            lead_source = st.selectbox("Lead Source", ["Website", "Referral", "Conference", "Cold Call", "Other"])
        with col2:
            last_name = st.text_input("Last Name", placeholder="Doe")
            company = st.text_input("Company", placeholder="Acme Corp")
            
        submit_btn = st.form_submit_button("Save Lead", type="primary")
        
        if submit_btn:
            if not first_name or not email:
                st.error("First Name and Email are required fields.")
            else:
                lead_id = add_lead(first_name, last_name, email, company, lead_source)
                st.success(f"Lead '{first_name} {last_name}' saved successfully!")
                time.sleep(1) # Brief pause so user sees the success message before rerun
                st.rerun()
