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
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        background-attachment: fixed;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        background-attachment: fixed;
    }
    
    .block-container {
        padding-top: 4rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Sidebar Premium */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    
    [data-testid="stSidebar"] .stImage {
        text-align: center;
        padding: 1rem 0;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #fff;
    }
    
    /* Metric Cards - Glassmorphism Premium */
    .premium-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .premium-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .premium-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .premium-card:hover::before {
        opacity: 1;
    }
    
    .metric-title {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    .metric-value-green {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    .metric-value-red {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    .metric-value-gold {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-header::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 1.5rem;
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 2px;
    }
    
    /* Streamlit Elements Override */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
    }
    
    .stDataFrame table {
        color: #e0e0e0 !important;
    }
    
    .stDataFrame th {
        background: rgba(102, 126, 234, 0.1) !important;
        color: #fff !important;
        font-weight: 600 !important;
    }
    
    .stDataFrame tr:hover td {
        background: rgba(102, 126, 234, 0.05) !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #fff !important;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: rgba(102, 126, 234, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stSelectbox>div>div>select {
        color: #fff !important;
    }
    
    .stSelectbox label, .stTextInput label, .stTextArea label {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500 !important;
    }
    
    .stExpander {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
    }
    
    .stExpander summary {
        color: #fff !important;
        font-weight: 600 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: rgba(255, 255, 255, 0.7) !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
        border-color: rgba(102, 126, 234, 0.5) !important;
        color: #fff !important;
    }
    
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
    }
    
    .stChatInput {
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    .stSuccess {
        background: rgba(17, 153, 142, 0.1) !important;
        border-color: rgba(17, 153, 142, 0.3) !important;
        color: #38ef7d !important;
    }
    
    .stError {
        background: rgba(235, 51, 73, 0.1) !important;
        border-color: rgba(235, 51, 73, 0.3) !important;
        color: #f45c43 !important;
    }
    
    .stInfo {
        background: rgba(102, 126, 234, 0.1) !important;
        border-color: rgba(102, 126, 234, 0.3) !important;
        color: #667eea !important;
    }
    
    /* Pipeline Cards */
    .pipeline-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .pipeline-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.5);
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Logo glow */
    .logo-glow {
        filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));
    }
    
    /* Chat bubbles */
    .chat-user {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .chat-ai {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
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
        title = {'text': title, 'font': {'size': 16, 'color': '#fff'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.3)"},
            'bar': {'color': color, 'thickness': 0.25},
            'bgcolor': "rgba(255,255,255,0.05)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': 'rgba(255,255,255,0.02)'}],
        }
    ))
    fig.update_layout(
        height=250, 
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#fff'}
    )
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
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <div style='
            font-size: 2.5rem; 
            margin-bottom: 0.5rem;
            filter: drop-shadow(0 0 15px rgba(102, 126, 234, 0.6));
        '>💎</div>
        <div style='
            font-size: 1.1rem; 
            font-weight: 700; 
            color: #fff;
            letter-spacing: 0.05em;
        '>NEXUS CRM</div>
        <div style='
            font-size: 0.7rem; 
            color: rgba(255,255,255,0.5); 
            text-transform: uppercase;
            letter-spacing: 0.15em;
        '>Enterprise Suite</div>
    </div>
    """, unsafe_allow_html=True)
    
    selected_menu = option_menu(
        menu_title="",
        options=["Home", "Contacts", "Campaigns", "Email", "Landing pages", "Events", "Leads", "Accounts", "Dashboards", "Marketing plans"],
        icons=["house", "person-badge", "megaphone", "envelope", "window", "balloon", "person-lines-fill", "building", "bar-chart", "calendar"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent", "margin": "0.5rem 0"},
            "icon": {"color": "#667eea", "font-size": "18px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"2px 0", "--hover-color": "rgba(102, 126, 234, 0.1)", "color": "rgba(255,255,255,0.7)", "border-radius": "8px"},
            "nav-link-selected": {"background": "linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2))", "color": "#fff", "border": "1px solid rgba(102, 126, 234, 0.3)", "border-radius": "8px", "font-weight": "600"},
        }
    )
    
    st.markdown("""
    <div style='
        margin-top: 2rem; 
        padding: 1rem; 
        text-align: center;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
    '>
        <div style='font-size: 0.7rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.1em;'>System Status</div>
        <div style='font-size: 0.8rem; color: #38ef7d; margin-top: 0.25rem; font-weight: 600;'>● All Systems Online</div>
    </div>
    """, unsafe_allow_html=True)

# --- GLOBAL LAYOUT: 3-PANE SPLIT ---
col_main, col_ai = st.columns([3, 1])

with col_main:
    # 1. HOME
    if selected_menu == "Home":
        st.markdown('<div class="section-header">Sales Manager Overview</div>', unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown('''
            <div class="premium-card">
                <div class="metric-title">Open Opportunities</div>
                <div class="metric-value">57</div>
            </div>
            ''', unsafe_allow_html=True)
            st.markdown('''
            <div class="premium-card">
                <div class="metric-title">Closed Won</div>
                <div class="metric-value-gold">$800,000</div>
            </div>
            ''', unsafe_allow_html=True)
        with m2:
            st.markdown('''
            <div class="premium-card">
                <div class="metric-title">Open Pipeline</div>
                <div class="metric-value">$4.97M</div>
            </div>
            ''', unsafe_allow_html=True)
            st.markdown('''
            <div class="premium-card">
                <div class="metric-title">Quota Gap</div>
                <div class="metric-value-red">20%</div>
            </div>
            ''', unsafe_allow_html=True)
        with m3:
            st.markdown('''
            <div class="premium-card">
                <div class="metric-title">Quota Target</div>
                <div class="metric-value">$1.0M</div>
            </div>
            ''', unsafe_allow_html=True)
            st.markdown('''
            <div class="premium-card">
                <div class="metric-title">At Risk Deals</div>
                <div class="metric-value-red">$200,000</div>
            </div>
            ''', unsafe_allow_html=True)
        with m4:
            st.markdown('''
            <div class="premium-card">
                <div class="metric-title">Win Rate</div>
                <div class="metric-value-green">68%</div>
            </div>
            ''', unsafe_allow_html=True)
            st.markdown('''
            <div class="premium-card">
                <div class="metric-title">Avg Deal Size</div>
                <div class="metric-value-gold">$42,500</div>
            </div>
            ''', unsafe_allow_html=True)
            
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.plotly_chart(create_gauge("Quota Attainment", 80, "#11998e"), use_container_width=True)
        with c2:
            with st.container(border=True):
                st.plotly_chart(create_gauge("Conversion Rate", 41, "#667eea"), use_container_width=True)

    # 2. CONTACTS
    elif selected_menu == "Contacts":
        st.markdown('<div class="section-header">Contact Directory</div>', unsafe_allow_html=True)
        st.dataframe(mock_contacts, hide_index=True, use_container_width=True)

    # 3. CAMPAIGNS (Interactive)
    elif selected_menu == "Campaigns":
        st.markdown('<div class="section-header">Q3 Campaign: No-code Days Miami</div>', unsafe_allow_html=True)
        c_left, c_right = st.columns([1, 2])
        with c_left:
            with st.expander("Campaign Info", expanded=True):
                st.markdown("**Name**\nCapturing audience for webinar: «marketing: several approaches on how to nurture your customer's leads»")
                st.caption("Goal")
                closed_deals = len(leads_df[leads_df['stage'] == 'Closed']) if not leads_df.empty else 0
                st.markdown(f'''
                <div class="premium-card">
                    <div class="metric-title">Reached the Goal</div>
                    <div class="metric-value-green">{closed_deals}</div>
                </div>
                <div class="premium-card">
                    <div class="metric-title">Participants (Total Leads)</div>
                    <div class="metric-value">{len(leads_df)}</div>
                </div>
                ''', unsafe_allow_html=True)
            with st.expander("Workflow Settings", expanded=True):
                st.markdown("**Start Mode**\nAt the specified time\n\n**Start Time**\n8/3/2026 2:51 PM")
                
        with c_right:
            tab_flow, tab_add = st.tabs(["📊 Campaign Flow", "➕ Add Participant"])
            with tab_flow:
                if leads_df.empty:
                    st.info("No leads in the pipeline. Click 'Add Participant' to get started!")
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
        st.markdown('<div class="section-header">Email Campaign Builder</div>', unsafe_allow_html=True)
        st.selectbox("To List", ["All Contacts", "Webinar Registrants", "Qualified Leads Only"])
        st.text_input("Subject Line", "Don't miss our Q3 Update!")
        st.text_area("Email Body", height=300, value="Hi {{first_name}},\n\nWe have some exciting news to share...\n\nBest,\nSales Team")
        st.button("Send Campaign", type="primary")

    # 5. LANDING PAGES
    elif selected_menu == "Landing pages":
        st.markdown('<div class="section-header">Landing Pages Performance</div>', unsafe_allow_html=True)
        st.dataframe(mock_landing_pages, hide_index=True, use_container_width=True)

    # 6. EVENTS
    elif selected_menu == "Events":
        st.markdown('<div class="section-header">Corporate Events Calendar</div>', unsafe_allow_html=True)
        st.dataframe(mock_events, hide_index=True, use_container_width=True)

    # 7. LEADS (Interactive)
    elif selected_menu == "Leads":
        st.markdown('<div class="section-header">Global Leads Database</div>', unsafe_allow_html=True)
        if not leads_df.empty:
            st.dataframe(leads_df, hide_index=True, use_container_width=True)
            st.download_button("Download CSV", data=leads_df.to_csv(index=False).encode('utf-8'), file_name='leads.csv', mime='text/csv')
            st.markdown("#### Activity Log")
            st.dataframe(activities_df, hide_index=True, use_container_width=True)
        else:
            st.info("No leads in database.")

    # 8. ACCOUNTS
    elif selected_menu == "Accounts":
        st.markdown('<div class="section-header">Managed Accounts</div>', unsafe_allow_html=True)
        st.dataframe(mock_accounts, hide_index=True, use_container_width=True)

    # 9. DASHBOARDS
    elif selected_menu == "Dashboards":
        st.markdown('<div class="section-header">Advanced Analytics</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            fig1 = px.bar(mock_landing_pages, x='Page Name', y='Page Views', title="Page Views by Campaign", color='Page Views', color_continuous_scale=['#667eea', '#764ba2'])
            fig1.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#fff'},
                title={'font': {'color': '#fff', 'size': 16}},
                xaxis={'gridcolor': 'rgba(255,255,255,0.05)', 'color': 'rgba(255,255,255,0.7)'},
                yaxis={'gridcolor': 'rgba(255,255,255,0.05)', 'color': 'rgba(255,255,255,0.7)'}
            )
            st.plotly_chart(fig1, use_container_width=True)
        with d2:
            fig2 = px.line(pd.DataFrame({'Date': pd.date_range(start='1/1/2026', periods=5, freq='ME'), 'Revenue': [10000, 15000, 12000, 22000, 28000]}), x='Date', y='Revenue', title="Monthly Revenue Trend", line_shape='spline')
            fig2.update_traces(line_color='#38ef7d', line_width=3)
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#fff'},
                title={'font': {'color': '#fff', 'size': 16}},
                xaxis={'gridcolor': 'rgba(255,255,255,0.05)', 'color': 'rgba(255,255,255,0.7)'},
                yaxis={'gridcolor': 'rgba(255,255,255,0.05)', 'color': 'rgba(255,255,255,0.7)'}
            )
            st.plotly_chart(fig2, use_container_width=True)

    # 10. MARKETING PLANS
    elif selected_menu == "Marketing plans":
        st.markdown('<div class="section-header">Marketing Roadmap</div>', unsafe_allow_html=True)
        st.dataframe(mock_marketing_plans, hide_index=True, use_container_width=True)


# --- RIGHT PANE: AI AGENT SIDEBAR ---
with col_ai:
    with st.container(border=True):
        st.markdown("""
        <div style='text-align: center; margin-bottom: 1rem;'>
            <div style='font-size: 2rem;'>🤖</div>
            <div style='font-weight: 700; color: #fff; margin-top: 0.5rem;'>Forecast Agent</div>
            <div style='font-size: 0.75rem; color: rgba(255,255,255,0.5);'>← Q4 Forecast Review</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        
        st.markdown('<div class="chat-user" style="padding: 1rem; border-radius: 12px; margin-bottom: 0.75rem;">', unsafe_allow_html=True)
        st.chat_message("user").write("How do I affect the sales forecast for this quarter?")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chat-ai" style="padding: 1rem; border-radius: 12px;">', unsafe_allow_html=True)
        st.chat_message("assistant").write("**Focus on closing high-potential opportunities:**\nThe 'Qualified' deals have significant drop-offs but represent deals close to closing.\n\n**Actions:**\n1. Identify high-value opportunities.\n2. Offer time-sensitive incentives.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        st.chat_input("Message to AI Agent...", key="ai_chat_input")
