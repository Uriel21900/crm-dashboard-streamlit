import streamlit as st
import pandas as pd
import time
from datetime import datetime
from sqlalchemy import text
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import plotly.express as px

# --- Constants & Config ---
st.set_page_config(
    page_title="Modern CRM",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
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
        color: #28a745;
        font-weight: 700;
    }
    .metric-value-blue {
        font-size: 36px;
        color: #007bff;
        font-weight: 700;
    }
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

def create_gauge(title, value, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': color, 'thickness': 0.25},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': '#f2f2f2'}],
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

leads_df = get_leads_df()
activities_df = get_activities_df()

# --- MOCK DATA FOR DEMO TABS ---
mock_contacts = pd.DataFrame({
    "Name": ["Sarah Connor", "Bruce Wayne", "Clark Kent", "Diana Prince", "Tony Stark"],
    "Role": ["Director of Security", "CEO", "Investigative Journalist", "Curator", "CTO"],
    "Company": ["Cyberdyne", "Wayne Enterprises", "Daily Planet", "Louvre", "Stark Industries"],
    "Phone": ["555-0192", "555-0101", "555-0123", "555-0144", "555-0199"],
    "Last Contacted": ["2026-08-10", "2026-08-14", "2026-08-01", "2026-08-15", "2026-07-30"]
})

mock_accounts = pd.DataFrame({
    "Account Name": ["Wayne Enterprises", "Stark Industries", "Daily Planet", "Cyberdyne", "Acme Corp"],
    "Industry": ["Defense", "Technology", "Media", "Robotics", "Manufacturing"],
    "Employees": ["10,000+", "5,000+", "500", "2,000", "1,500"],
    "Annual Revenue": ["$1.2B", "$2.5B", "$50M", "$400M", "$150M"],
    "Account Owner": ["Alice", "Bob", "Alice", "Charlie", "Bob"]
})

mock_landing_pages = pd.DataFrame({
    "Page Name": ["Q3 Webinar Sign-up", "Main Product Demo", "Newsletter Opt-in", "E-book Download"],
    "Status": ["🟢 Active", "🟢 Active", "🟢 Active", "🔴 Paused"],
    "Page Views": [3420, 15000, 890, 4500],
    "Conversions": [677, 1200, 400, 900],
    "Conversion Rate": ["19.8%", "8.0%", "44.9%", "20.0%"]
})

mock_events = pd.DataFrame({
    "Event Name": ["No-code days Miami", "Q4 Sales Kickoff", "Tech Expo 2026", "Executive Dinner"],
    "Type": ["Conference", "Internal", "Trade Show", "Networking"],
    "Date": ["Oct 12, 2026", "Dec 01, 2026", "Nov 15, 2026", "Sep 20, 2026"],
    "Registered": [677, 120, 450, 25]
})

mock_marketing_plans = pd.DataFrame({
    "Campaign": ["Email Nurture Track", "LinkedIn Ads", "SEO Optimization", "Webinar Series"],
    "Budget": ["$5,000", "$25,000", "$10,000", "$15,000"],
    "Start Date": ["Aug 01, 2026", "Sep 01, 2026", "Jul 15, 2026", "Oct 01, 2026"],
    "Status": ["In Progress", "Planning", "In Progress", "Planning"]
})

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png", width=50) # Placeholder Logo
    
    selected_menu = option_menu(
        menu_title="All apps",
        options=["Home", "Contacts", "Campaigns", "Email", "Landing pages", "Events", "Leads", "Accounts", "Dashboards", "Marketing plans"],
        icons=["house", "person-badge", "megaphone", "envelope", "window", "balloon", "person-lines-fill", "building", "bar-chart", "calendar"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#a0a0a0", "font-size": "18px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#333"},
            "nav-link-selected": {"background-color": "#444"},
        }
    )

# --- GLOBAL LAYOUT: 3-PANE SPLIT ---
col_main, col_ai = st.columns([3, 1])

with col_main:
    # 1. HOME
    if selected_menu == "Home":
        st.markdown("### Sales manager homepage")
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown('<div class="metric-card"><div class="metric-title"># Open opportunities</div><div class="metric-value-blue">57</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-card"><div class="metric-title">$ Closed won</div><div class="metric-value-blue">800,000</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="metric-card"><div class="metric-title">$ Open pipeline</div><div class="metric-value-blue">4,966,548</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-card"><div class="metric-title">% Quota gap</div><div style="font-size: 36px; color: #dc3545; font-weight: 700;">20</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown('<div class="metric-card"><div class="metric-title">$ Quota Target</div><div class="metric-value-blue">1,000,000</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-card"><div class="metric-title">$ At Risk Deals</div><div style="font-size: 36px; color: #dc3545; font-weight: 700;">200,000</div></div>', unsafe_allow_html=True)
            
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.plotly_chart(create_gauge("% Quota attainment", 80, "#28a745"), use_container_width=True)
        with c2:
            with st.container(border=True):
                st.plotly_chart(create_gauge("% Conversion rate", 41, "#28a745"), use_container_width=True)

    # 2. CONTACTS
    elif selected_menu == "Contacts":
        st.markdown("### Contact Directory")
        st.dataframe(mock_contacts, hide_index=True, use_container_width=True)

    # 3. CAMPAIGNS (Interactive)
    elif selected_menu == "Campaigns":
        st.markdown("### ← Q3 'No-code days Miami' event invitation & products promotion campaign")
        c_left, c_right = st.columns([1, 2])
        with c_left:
            with st.expander("Campaign info", expanded=True):
                st.markdown("**Name\\***\nCapturing audience for webinar: «marketing: several approaches on how to nurture your customer's leads»")
                st.caption("Goal")
                closed_deals = len(leads_df[leads_df['stage'] == 'Closed']) if not leads_df.empty else 0
                st.markdown(f'<div class="metric-card"><div class="metric-title">Reached the goal</div><div class="metric-value-green">{closed_deals}</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><div class="metric-title">Participants (Total Leads)</div><div class="metric-value-blue">{len(leads_df)}</div></div>', unsafe_allow_html=True)
            with st.expander("Workflow settings", expanded=True):
                st.markdown("**Start mode**\nAt the specified time\n\n**Start time**\n8/3/2026 2:51 PM")
                
        with c_right:
            tab_flow, tab_add = st.tabs(["CAMPAIGN FLOW (Pipeline)", "➕ ADD PARTICIPANT"])
            with tab_flow:
                if leads_df.empty:
                    st.info("No leads in the pipeline. Click '➕ ADD PARTICIPANT' to get started!")
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
                                    ca, cb = st.columns(2)
                                    with ca:
                                        if i > 0 and st.button("⬅️", key=f"p_{lead['id']}"):
                                            update_lead_stage(lead['id'], STAGES[i-1])
                                            st.rerun()
                                    with cb:
                                        if i < len(STAGES) - 1 and st.button("➡️", key=f"n_{lead['id']}"):
                                            update_lead_stage(lead['id'], STAGES[i+1])
                                            st.rerun()
                                    with st.expander("AI Email"):
                                        if st.button("Generate Draft", key=f"ai_{lead['id']}"):
                                            with st.spinner("AI drafting..."):
                                                subj, body = mock_ai_generate_email(lead['first_name'], lead['company'], lead['lead_source'])
                                                st.session_state[f"d_s_{lead['id']}"] = subj
                                                st.session_state[f"d_b_{lead['id']}"] = body
                                        if f"d_s_{lead['id']}" in st.session_state:
                                            st.text_input("Subject", value=st.session_state[f"d_s_{lead['id']}"], key=f"i_s_{lead['id']}")
                                            st.text_area("Body", value=st.session_state[f"d_b_{lead['id']}"], height=200, key=f"i_b_{lead['id']}")
                                            if st.button("Send Email", key=f"s_{lead['id']}"):
                                                log_activity(lead['id'], "Email", f"Sent: {st.session_state[f'd_s_{lead['id']}']}")
                                                st.success("Sent!")
                                                st.rerun()
            with tab_add:
                with st.form("lead_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    first_name = c1.text_input("First Name")
                    email = c1.text_input("Email Address")
                    lead_source = c1.selectbox("Lead Source", ["Website", "Referral", "Conference", "Cold Call", "Other"])
                    last_name = c2.text_input("Last Name")
                    company = c2.text_input("Company")
                    if st.form_submit_button("Save Participant", type="primary"):
                        if not first_name or not email:
                            st.error("First Name and Email are required.")
                        else:
                            add_lead(first_name, last_name, email, company, lead_source)
                            st.success("Participant added successfully!")
                            time.sleep(1)
                            st.rerun()

    # 4. EMAIL
    elif selected_menu == "Email":
        st.markdown("### Email Campaign Builder")
        st.selectbox("To List", ["All Contacts", "Webinar Registrants", "Qualified Leads Only"])
        st.text_input("Subject Line", "Don't miss our Q3 Update!")
        st.text_area("Email Body", height=300, value="Hi {{first_name}},\n\nWe have some exciting news to share...\n\nBest,\nSales Team")
        st.button("Send Campaign", type="primary")

    # 5. LANDING PAGES
    elif selected_menu == "Landing pages":
        st.markdown("### Landing Pages Performance")
        st.dataframe(mock_landing_pages, hide_index=True, use_container_width=True)

    # 6. EVENTS
    elif selected_menu == "Events":
        st.markdown("### Corporate Events Calendar")
        st.dataframe(mock_events, hide_index=True, use_container_width=True)

    # 7. LEADS (Interactive)
    elif selected_menu == "Leads":
        st.markdown("### Global Leads Database")
        if not leads_df.empty:
            st.dataframe(leads_df, hide_index=True, use_container_width=True)
            st.download_button("Download CSV", data=leads_df.to_csv(index=False).encode('utf-8'), file_name='leads.csv', mime='text/csv')
            st.markdown("#### Activity Log")
            st.dataframe(activities_df, hide_index=True, use_container_width=True)
        else:
            st.info("No leads in database.")

    # 8. ACCOUNTS
    elif selected_menu == "Accounts":
        st.markdown("### Managed Accounts")
        st.dataframe(mock_accounts, hide_index=True, use_container_width=True)

    # 9. DASHBOARDS
    elif selected_menu == "Dashboards":
        st.markdown("### Advanced Analytics")
        d1, d2 = st.columns(2)
        with d1:
            st.plotly_chart(px.bar(mock_landing_pages, x='Page Name', y='Page Views', title="Page Views by Campaign"), use_container_width=True)
        with d2:
            st.plotly_chart(px.line(pd.DataFrame({'Date': pd.date_range(start='1/1/2026', periods=5, freq='ME'), 'Revenue': [10000, 15000, 12000, 22000, 28000]}), x='Date', y='Revenue', title="Monthly Revenue Trend"), use_container_width=True)

    # 10. MARKETING PLANS
    elif selected_menu == "Marketing plans":
        st.markdown("### Marketing Roadmap")
        st.dataframe(mock_marketing_plans, hide_index=True, use_container_width=True)


# --- RIGHT PANE: AI AGENT SIDEBAR ---
with col_ai:
    with st.container(border=True, height=800):
        st.markdown("#### 🤖 Forecast Agent")
        st.caption("← Q4 Forecast Review")
        st.divider()
        st.chat_message("user").write("How do I affect the sales forecast for this quarter?")
        st.chat_message("assistant").write("**Focus on closing high-potential opportunities:**\nThe 'Qualified' deals have significant drop-offs but represent deals close to closing.\n\n**Actions:**\n1. Identify high-value opportunities.\n2. Offer time-sensitive incentives.")
        st.divider()
        st.chat_input("Message to AI Agent...", key="ai_chat_input")
