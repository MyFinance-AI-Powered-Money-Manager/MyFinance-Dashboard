import streamlit as st
import plotly.graph_objects as go
import requests
from dotenv import load_dotenv
from utils import format_currency, format_percentage, get_month_start_end, get_past_month, get_month_name, to_dataframe, get_leak_and_score, extract_data

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MyFinance Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Green brand theme */
    [data-testid="stSidebar"] {
        background-color: #f0fdf4;
    }
    .stMetric value {
        color: #0A5C36;
    }
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0A5C36;
        margin-bottom: -10px;
    }
    .sub-header {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .card-box {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
        margin-bottom: 20px;
    }
    .badge-green { background-color: #dcfce7; color: #16a34a; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
    .badge-red { background-color: #fee2e2; color: #dc2626; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
if "USERID" in st.query_params:
    date = get_month_start_end()
    userid = st.query_params.get("USERID")
    template_url = st.secrets['URL_BACKEND_MYFINANCE']
    url = template_url.format(userid, date['start_date'], date['end_date'])
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        leak_and_score_data = get_leak_and_score(data)
    else:
        st.write(f"Failed get data {response.status_code}")
    try:
        extracted_data = extract_data(data)
    except:
        st.error("Can't get current month's data, trying with past month's data")
        if "USERID" in st.query_params:
            date = get_past_month()
            userid = st.query_params.get("USERID")
            url = template_url.format(userid, date['start_date'], date['end_date'])
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                leak_and_score_data = get_leak_and_score(data)
            else:
                st.write(f"Failed get data {response.status_code}")
else:
    st.write("Please put in id parameter")
    st.stop()

extracted_data = extract_data(data)

# --- SIDEBAR NAV ---
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-top: 10px;">
    <svg width="42" height="42" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="20" cy="20" r="20" fill="#0A5C36"/>
        <path d="M25 14H15C13.3431 14 12 15.3431 12 17V23C12 24.6569 13.3431 26 15 26H25C26.6569 26 28 24.6569 28 23V17C28 15.3431 26.6569 14 25 14Z" fill="white"/>
        <path d="M28 17.5V22.5C28 23.3284 27.3284 24 26.5 24H18.5C17.6716 24 17 23.3284 17 22.5V17.5C17 16.6716 17.6716 16 18.5 16H26.5C27.3284 16 28 16.6716 28 17.5Z" fill="#0A5C36"/>
        <path d="M26.5 17.5V22.5C26.5 22.7761 26.2761 23 26 23H20C19.7239 23 19.5 22.7761 19.5 22.5V17.5C19.5 17.2239 19.7239 17 20 17H26C26.2761 17 26.5 17.2239 26.5 17.5Z" fill="white"/>
        <circle cx="23" cy="20" r="1.5" fill="#0A5C36"/>
    </svg>
    <span style="font-size: 26px; font-weight: 800; color: #0A5C36; letter-spacing: -0.5px; font-family: 'Inter', sans-serif;">MyFinance</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("**Welcome back**", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Leak Detection", "Budget & Risk", "Weekly Rewind"])

st.sidebar.markdown("---")
st.sidebar.caption("Period")
st.sidebar.markdown(f"**📅 {get_month_name(extracted_data['current_month_year'])}**")

# --- VIEWS ---
def render_financial_overview():
    st.markdown("##### Financial Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Income", format_currency(extracted_data['metrics']['total_income']))
    with col2:
        st.metric("Total Expense", format_currency(extracted_data['metrics']['total_expense']))
    with col3:
        st.metric("Net Cashflow", format_currency(extracted_data['metrics']['net_cashflow']))
    with col4:
        st.metric("Savings Rate", format_percentage(extracted_data['metrics']['savings_rate']))
    st.markdown("---")

def render_health_score():
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("##### Financial Health Score")
        score = extracted_data['financial_score']
        category = extracted_data['metrics']['score_category']
        
        # Plotly Gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#22c55e" if score >= 80 else "#14b8a6" if score >= 60 else "#f59e0b"},
                'steps': [
                    {'range': [0, 40], 'color': "#fee2e2"},
                    {'range': [40, 60], 'color': "#fef3c7"},
                    {'range': [60, 80], 'color': "#ccfbf1"},
                    {'range': [80, 100], 'color': "#dcfce7"}
                ]
            }
        ))
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width='stretch')
        
        st.caption(f"**Category:** {category}")
        
    with col2:
        st.markdown("##### Score Reason")
        st.info(extracted_data['metrics']['score_reason'])
        
        leak_products = extracted_data['leak_products']
        leak_df = extracted_data['leak_df']
        if len(leak_products) > 0:
            for i in leak_products:
                product_price = int(leak_df.loc[leak_df['product'] == i, 'amount'].iloc[0])
                st.warning(f"**{i}** appears as a potential leak with **{format_currency(product_price)}** total spending")

def render_metric_breakdown():
    st.markdown("##### Metric Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    with col1:  
        st.metric("Needs Ratio", format_percentage(extracted_data['metrics']['needs_ratio']))
    with col2:
        st.metric("Wants Ratio", format_percentage(extracted_data['metrics']['wants_ratio']))
    with col3:
        st.metric("Budget Used", format_percentage(extracted_data['metrics']['budget_used_ratio']))
    with col4:
        st.metric("Overbudget Cats", extracted_data['metrics']['overbudget_category_count'])

def render_leak_table():
    st.markdown("##### Leak Analysis Table")
    leak_products_count = len(extracted_data['leak_products'])
    if leak_products_count > 0:
        df = extracted_data['leak_df']
        st.dataframe(df)
    else:
        st.info("No leak data available.")

def render_budget_and_spending():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Budget Risk")
        # if budget_summary:
        #     for item in budget_summary:
        #         st.markdown(f"**{item['category']}** ({item['risk_level']})")
        #         st.progress(min(1.0, item['budget_used_ratio']))
        #         st.caption(f"Used: {format_currency(item['actual_spending'])} / {format_currency(item['limit_amount'])}")
        # else:
        #     st.info("Budget data not available.")
        # Revised
        budget_dict = extracted_data['budget']
        for category in budget_dict:
            st.markdown(f"**{category}**")
            if category == 'NEEDS':
                st.progress(min(1.0, extracted_data['metrics']['needs_ratio']))
                st.caption(f"Used: {format_currency(extracted_data['needs_spending'])}")
            elif category == 'WANTS':
                st.progress(min(1.0, extracted_data['metrics']['wants_ratio']))
                st.caption(f"Used: {format_currency(extracted_data['wants_spending'])}")
            elif category == 'OTHERS':
                st.progress(min(1.0, extracted_data['metrics']['others_ratio']))
                st.caption(f"Used: {format_currency(extracted_data['others_spending'])}")
            
    with col2:
        st.markdown("##### Daily Spending Trend")
        if len(extracted_data['daily_spending']) > 0:
            df_trend = extracted_data['daily_spending']
            st.line_chart(df_trend.set_index('timestamp')['amount'], color="#16a34a")
        else:
            st.info("Daily spending data not available.")

def render_recent_transactions():
    st.markdown("##### Recent Transactions")
    if len(extracted_data['spending_data']) > 0:
        st.dataframe(extracted_data['spending_data'], width='stretch')
    else:
        st.info("No recent transactions.")

def render_weekly_rewind():
    weekly_summary = extracted_data['weekly_summary']
    weekly_percentages = extracted_data['weekly_summary_percentages']
    for i in range(0, len(weekly_percentages)):
        with st.container(border=True):
            st.markdown(f"#### {weekly_summary.iloc[i, 12]} ({weekly_summary.iloc[i, 11]} - {weekly_summary.iloc[i, 10]})")
            col1, col2, col3, col4 = st.columns(4)
            col5, col6, col7, col8 = st.columns(4)
            with col1:
                st.metric('Total Spending', format_currency(weekly_summary.iloc[i, 1]))
            with col2:
                st.metric('Hobi & Self Reward', format_currency(weekly_summary.iloc[i, 2]))
                st.caption(f"{weekly_percentages.iloc[i, 6]}%")
            with col3:
                st.metric('Jajan & Nongkrong', format_currency(weekly_summary.iloc[i, 3]))
                st.caption(f"{weekly_percentages.iloc[i, 7]}%")
            with col4:
                st.metric('Kebutuhan Rumah & Mandi', format_currency(weekly_summary.iloc[i, 4]))
                st.caption(f"{weekly_percentages.iloc[i, 8]}%")
            with col5:
                st.metric('Lain-lain & Darurat', format_currency(weekly_summary.iloc[i, 5]))
                st.caption(f"{weekly_percentages.iloc[i, 9]}%")
            with col6:
                st.metric('Makan & Minum Harian', format_currency(weekly_summary.iloc[i, 6]))
                st.caption(f"{weekly_percentages.iloc[i, 10]}%")
            with col7:
                st.metric('Tagihan & Kewajiban', format_currency(weekly_summary.iloc[i, 7]))
                st.caption(f"{weekly_percentages.iloc[i, 11]}%")
            with col8:
                st.metric('Transportasi & Rutinitas', format_currency(weekly_summary.iloc[i, 8]))
                st.caption(f"{weekly_percentages.iloc[i, 12]}%")

# --- MAIN ROUTING ---
if menu == "Dashboard":
    st.markdown('<div class="main-header">MyFinance Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Monitor your financial health, detect leaks, and track spending behavior.</div>', unsafe_allow_html=True)
    render_financial_overview()
    render_health_score()
    st.markdown("---")
    render_metric_breakdown()

elif menu == "Leak Detection":
    st.markdown('<div class="main-header">Leak Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Identify and manage repetitive small expenses that add up over time.</div>', unsafe_allow_html=True)
    render_leak_table()

elif menu == "Budget & Risk":
    st.markdown('<div class="main-header">Budget & Risk</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Track budget usage, spending trends, and overbudget risk per category.</div>', unsafe_allow_html=True)
    render_budget_and_spending()
    st.markdown("---")
    render_recent_transactions()

elif menu == "Weekly Rewind":
    st.markdown('<div class="main-header">Weekly Rewind</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your weekly financial recap with AI-powered insights.</div>', unsafe_allow_html=True)
    render_weekly_rewind()

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 MyFinance. All rights reserved.")