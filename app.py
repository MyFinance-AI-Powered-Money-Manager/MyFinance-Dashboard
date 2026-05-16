import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_data, format_currency, format_percentage, get_month_name

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
data = load_data()
if not data:
    st.error("Failed to load dashboard data.")
    st.stop()

financial_score = data.get("financial_score", {})
metrics = financial_score.get("metrics", {})
leak_detection = data.get("leak_detection", {})
weekly_rewind = data.get("weekly_rewind", {})
budget_summary = data.get("budget_summary", [])
spending_breakdown = data.get("spending_breakdown", [])
daily_spending = data.get("daily_spending", [])
recent_transactions = data.get("recent_transactions", [])
month_period = data.get("month_period", "")

# --- SIDEBAR NAV ---
st.sidebar.image("https://ui-avatars.com/api/?name=Robby&background=0A5C36&color=fff", width=60)
st.sidebar.markdown("**Welcome back**<br><span style='color:gray; font-size:12px;'>Financial Sanctuary</span>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Leak Detection", "Budget & Risk", "Weekly Rewind"])

st.sidebar.markdown("---")
st.sidebar.caption("Period")
st.sidebar.markdown(f"**📅 {get_month_name(month_period)}**")

# --- VIEWS ---
def render_financial_overview():
    st.markdown("##### Financial Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Income", format_currency(metrics.get("total_income")))
    with col2:
        st.metric("Total Expense", format_currency(metrics.get("total_expense")))
    with col3:
        st.metric("Net Cashflow", format_currency(metrics.get("net_cashflow")))
    with col4:
        st.metric("Savings Rate", format_percentage(metrics.get("savings_rate")))
    st.markdown("---")

def render_health_score():
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("##### Financial Health Score")
        score = financial_score.get("financial_score", 0)
        category = financial_score.get("score_category", "")
        
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
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption(f"**Category:** {category}")
        
    with col2:
        st.markdown("##### AI Insight")
        st.info(f"🤖 **Analysis:** {financial_score.get('score_reason', 'Data is being analyzed.')}")
        
        summary = leak_detection.get("summary", {})
        if summary.get("final_potential_leak_count", 0) > 0:
            st.warning(f"**{summary.get('top_leak_item')}** appears as a potential leak with **{format_currency(summary.get('top_leak_total_spending'))}** total spending.")

def render_metric_breakdown():
    st.markdown("##### Metric Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Needs Ratio", format_percentage(metrics.get("needs_ratio")))
    with col2:
        st.metric("Wants Ratio", format_percentage(metrics.get("wants_ratio")))
    with col3:
        st.metric("Budget Used", format_percentage(metrics.get("budget_used_ratio_total")))
    with col4:
        st.metric("Overbudget Cats", metrics.get("overbudget_category_count", 0))

def render_leak_table():
    st.markdown("##### Leak Analysis Table")
    leaks = leak_detection.get("leaks", [])
    if leaks:
        df = pd.DataFrame(leaks)
        df_display = df[['description', 'category', 'frequency', 'total_spending', 'rule_leak_type', 'is_final_potential_leak']]
        df_display.columns = ['Item', 'Category', 'Freq', 'Total (Rp)', 'Type', 'Is Leak?']
        
        # Color coding for dataframe
        def color_leak(val):
            color = '#dc2626' if val == 1 else '#16a34a'
            return f'color: {color}'
            
        st.dataframe(df_display.style.map(color_leak, subset=['Is Leak?']), use_container_width=True)
    else:
        st.info("No leak data available.")

def render_budget_and_spending():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Budget Risk")
        if budget_summary:
            for item in budget_summary:
                st.markdown(f"**{item['category']}** ({item['risk_level']})")
                st.progress(min(1.0, item['budget_used_ratio']))
                st.caption(f"Used: {format_currency(item['actual_spending'])} / {format_currency(item['limit_amount'])}")
        else:
            st.info("Budget data not available.")
            
    with col2:
        st.markdown("##### Daily Spending Trend")
        if daily_spending:
            df_trend = pd.DataFrame(daily_spending)
            st.line_chart(df_trend.set_index('date')['amount'], color="#16a34a")
        else:
            st.info("Daily spending data not available.")

def render_recent_transactions():
    st.markdown("##### Recent Transactions")
    if recent_transactions:
        df_tx = pd.DataFrame(recent_transactions)
        df_tx = df_tx[['transaction_date', 'description', 'category', 'total_amount', 'type']]
        df_tx.columns = ['Date', 'Description', 'Category', 'Amount (Rp)', 'Type']
        st.dataframe(df_tx, use_container_width=True)
    else:
        st.info("No recent transactions.")

def render_weekly_rewind():
    st.markdown("##### Weekly Rewind")
    if weekly_rewind:
        col1, col2, col3 = st.columns(3)
        col1.metric("Income", format_currency(weekly_rewind.get('weekly_income')))
        col2.metric("Expense", format_currency(weekly_rewind.get('weekly_expense')))
        col3.metric("Net Cashflow", format_currency(weekly_rewind.get('weekly_net_cashflow')))
        
        st.markdown(f"**Top Category:** {weekly_rewind.get('top_category')} ({format_currency(weekly_rewind.get('top_category_spending'))})")
        st.markdown(f"**Top Leak Item:** {weekly_rewind.get('top_leak_item')}")
        st.info(f"💡 {weekly_rewind.get('weekly_insight')}")
    else:
        st.info("Weekly rewind data not available.")

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
st.sidebar.caption("© 2024 MyFinance. All rights reserved.")
