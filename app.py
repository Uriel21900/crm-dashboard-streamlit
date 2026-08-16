import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime
import os

# --- Constants & Config ---
DB_PATH = 'crm_database.db'

st.set_page_config(
    page_title="Automated Email/CRM Dashboard",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            company TEXT,
            lead_source TEXT,
            status TEXT,
            created_at TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            subject TEXT,
            body TEXT,
            sent_at TIMESTAMP,
            status TEXT,
            FOREIGN KEY (lead_id) REFERENCES leads (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Helper Functions ---
def get_db_connection():
    return sqlite3.connect(DB_PATH)

def add_lead(first_name, last_name, email, company, lead_source):
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now()
    cursor.execute('''
        INSERT INTO leads (first_name, last_name, email, company, lead_source, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (first_name, last_name, email, company, lead_source, 'New', created_at))
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return lead_id

def log_email(lead_id, subject, body, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    sent_at = datetime.now()
    cursor.execute('''
        INSERT INTO emails (lead_id, subject, body, sent_at, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (lead_id, subject, body, sent_at, status))
    conn.commit()
    conn.close()

def get_leads_df():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM leads ORDER BY created_at DESC", conn)
    conn.close()
    return df

def simulate_send_email(lead_name, email_address, company):
    # Simulate network delay and sending process
    subject = f"Welcome to our platform, {lead_name}!"
    body = f"Hi {lead_name},\n\nThank you for your interest from {company}. We are excited to have you onboard.\n\nBest,\nSales Team"
    
    with st.spinner(f"Sending automated welcome email to {email_address}..."):
        time.sleep(2) # Simulate delay
        
    return subject, body

# --- UI Components ---
st.title("💼 Automated Email & CRM Dashboard")
st.markdown("A simple dashboard to input lead information, save it to a local SQLite database, and automatically send a simulated welcome email.")

# Sidebar for Navigation / Stats
with st.sidebar:
    st.header("📊 Dashboard Stats")
    leads_df = get_leads_df()
    st.metric("Total Leads", len(leads_df))
    st.metric("Emails Sent", len(leads_df[leads_df['status'] == 'Emailed']) if not leads_df.empty else 0)
    st.divider()
    st.info("This is a demo application. Emails are simulated and not actually sent over the network.")

# Main Layout
tab1, tab2 = st.tabs(["➕ Add New Lead", "📋 View Lead Database"])

with tab1:
    st.subheader("Lead Entry Form")
    with st.form("lead_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", placeholder="Jane")
            email = st.text_input("Email Address", placeholder="jane@company.com")
            lead_source = st.selectbox("Lead Source", ["Website", "Referral", "Conference", "Cold Call", "Other"])
        with col2:
            last_name = st.text_input("Last Name", placeholder="Doe")
            company = st.text_input("Company", placeholder="Acme Corp")
            auto_email = st.checkbox("Automatically Send Welcome Email", value=True)
            
        submit_btn = st.form_submit_button("Save Lead & Process")
        
        if submit_btn:
            if not first_name or not email:
                st.error("First Name and Email are required fields.")
            else:
                # 1. Save Lead
                lead_id = add_lead(first_name, last_name, email, company, lead_source)
                st.success(f"Lead '{first_name} {last_name}' saved successfully!")
                
                # 2. Automated Email Workflow
                if auto_email:
                    subject, body = simulate_send_email(first_name, email, company)
                    log_email(lead_id, subject, body, 'Sent')
                    
                    # Update Lead Status
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE leads SET status = 'Emailed' WHERE id = ?", (lead_id,))
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Simulated email sent successfully to **{email}**!")
                    with st.expander("View Email Content"):
                        st.write(f"**Subject:** {subject}")
                        st.text(body)

with tab2:
    st.subheader("CRM Database")
    st.markdown("Here you can view the structured data saved in the SQLite database.")
    
    current_leads_df = get_leads_df()
    if current_leads_df.empty:
        st.info("No leads found. Add a lead in the 'Add New Lead' tab.")
    else:
        st.dataframe(
            current_leads_df,
            column_config={
                "id": "Lead ID",
                "first_name": "First Name",
                "last_name": "Last Name",
                "email": "Email",
                "company": "Company",
                "lead_source": "Source",
                "status": "Status",
                "created_at": st.column_config.DatetimeColumn("Date Added", format="D MMM YYYY, h:mm a"),
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Download Data feature
        csv = current_leads_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name='crm_leads.csv',
            mime='text/csv',
        )
