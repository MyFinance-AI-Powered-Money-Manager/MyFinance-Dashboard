import json
import os
import calendar
import requests
import pandas as pd
from dotenv import load_dotenv
import datetime

load_dotenv()

def format_currency(value):
    if value is None:
        return "Rp0"
    return f"Rp{value:,.0f}".replace(',', '.')

def format_percentage(value):
    if value is None:
        return "0%"
    return f"{value * 100:.0f}%"

def get_month_name(month_str):
    months = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
        '05': 'Mei', '06': 'Jun', '07': 'Jul', '08': 'Agu',
        '09': 'Sep', '10': 'Okt', '11': 'Nov', '12': 'Des'
    }
    try:
        year, month = month_str.split('-')
        return f"{months.get(month, month)} {year}"
    except:
        return month_str

def get_past_month():
    # Get today's date
    today = datetime.date.today()

    # Get the first day of the CURRENT month
    first_of_current = today.replace(day=1)

    # Subtract 1 day to get the LAST day of the PAST month
    last_of_past = first_of_current - datetime.timedelta(days=1)

    # Change the day to 1 to get the FIRST day of the PAST month
    first_of_past = last_of_past.replace(day=1)

    # Format with underscores (YYYY_MM_DD)
    past_start= first_of_past.strftime('%Y_%m_%d')
    past_end = last_of_past.strftime('%Y_%m_%d')
    
    return {
        'start_date': past_start,
        'end_date': past_end
    }


def get_month_start_end():
    # Get today's date
    today = datetime.date.today()

    # Get current month start date
    start_date = today.replace(day=1)

    # Get the end date of the current month
    _, last_day = calendar.monthrange(today.year, today.month)
    end_date = today.replace(day=last_day)

    # Format date with underscores (YYYY_MM_DD)
    start_date_underscore = start_date.strftime('%Y_%m_%d')
    end_date_underscore = end_date.strftime('%Y_%m_%d')

    return {
        'start_date': start_date_underscore,
        'end_date': end_date_underscore,
    }

def get_leak_and_score(data):
    data['month_period'] = '2026'
    payload = data
    url_leak_FS = os.getenv('URL_LEAK_FS')
    response_leak_FS = requests.post(url_leak_FS, json=payload)
    return response_leak_FS.json()

def to_dataframe(df_items, df_transactions):
    df_items.drop(columns=['id'], inplace=True)
    df_items.rename(columns={'transaction_id': 'id'}, inplace=True)
    df_joined = pd.merge(
    df_items, 
    df_transactions[['id', 'type', 'transaction_date']], 
    left_on='id', 
    right_on='id', 
    how='inner'
    )

    df_joined.drop(columns=['id'], inplace=True)
    df_joined.rename(columns=
                    {
                        'transaction_date': 'timestamp',
                        'item_name': 'title',
                        'subcategory': 'master_category',
                        'category': 'macro_category',
                        'price': 'amount',
                    }, inplace=True)
    return df_joined

def get_ordinal_suffix(day):
    if 11 <= day <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

def date_to_string(df):
    df['start_date'] = df['end_date'] - pd.Timedelta(days=6)
    # Change start date
    months = df['end_date'].dt.strftime('%B')
    days = df['end_date'].dt.day
    suffixes = days.apply(get_ordinal_suffix)
    df['end_string'] = months + ' ' + days.astype(str) + suffixes
    # Change end date
    months = df['start_date'].dt.strftime('%B')
    days = df['start_date'].dt.day
    suffixes = days.apply(get_ordinal_suffix)
    df['start_string'] = months + ' ' + days.astype(str) + suffixes

def get_weekly_summary(df):
    df_expense = df[df['type'] == 'EXPENSE']
    df_expense.rename(columns={
        'timestamp': 'date'
    }, inplace=True)
    df_expense['date'] = pd.to_datetime(df_expense['date'])
    weekly_total = df_expense.groupby(pd.Grouper(key='date', freq='W'))['amount'].sum().reset_index()

    weekly_by_category = df_expense.pivot_table(
    index=pd.Grouper(key='date', freq='W'),
    columns='master_category',
    values='amount',
    aggfunc='sum',
    fill_value=0  # Fills weeks with no category spend with 0 instead of NaN
    ).reset_index()

    weekly_summary = pd.merge(weekly_total, weekly_by_category, on='date')
    weekly_summary.rename(columns={'amount': 'total_amount'}, inplace=True)
    
    weekly_summary.rename(columns={
        'date':'end_date'
        }, inplace=True)
    
    date_to_string(weekly_summary)

    weekly_summary['week'] = [f"week {i}" for i in range(1, len(weekly_summary) + 1)]

    return weekly_summary

def get_weekly_summary_percentages(weekly_summary):
    metadata_cols = ['start_date', 'end_date', 'start_string', 'end_string', 'total_amount', 'week']
    category_cols = [col for col in weekly_summary.columns if col not in metadata_cols]

    weekly_summary['total_amount'] = pd.to_numeric(weekly_summary['total_amount'], errors='coerce')

    for col in category_cols:
        weekly_summary[col] = pd.to_numeric(weekly_summary[col], errors='coerce')

    weekly_percentages = weekly_summary[metadata_cols].copy()

    weekly_percentages[category_cols] = (
        weekly_summary[category_cols]
        .div(weekly_summary['total_amount'], axis=0) * 100
    ).fillna(0).round(2)
    return weekly_percentages

def extract_data(data):
    # Join data into compatible dataframe
    df_items = pd.DataFrame(data['transaction_items'])
    df_transactions = pd.DataFrame(data['transactions'])
    df_budgets = pd.DataFrame(data['budgets'])
    df = to_dataframe(df_items, df_transactions)
    # Get leak and financial score
    leak_score_data = get_leak_and_score(data)
    # Financial Score
    financial_score = leak_score_data['financial summary']['financial_score']
    # Metrics
    metrics = {'total_expense':leak_score_data['financial summary']['total_expense'],
           'total_income':leak_score_data['financial summary']['total_income'],
           'net_cashflow':leak_score_data['financial summary']['net_cashflow'],
           'savings_rate':leak_score_data['financial summary']['savings_rate'],
           'needs_ratio':leak_score_data['financial summary']['needs_ratio'],
           'wants_ratio':leak_score_data['financial summary']['wants_ratio'],
           'others_ratio':leak_score_data['financial summary']['wants_ratio'],
           'budget_used_ratio':leak_score_data['financial summary']['budget_used_ratio_total'],
           'overbudget_category_count':leak_score_data['financial summary']['overbudget_category_count'],
           'score_category':leak_score_data['financial summary']['score_category'],
           'score_reason':leak_score_data['financial summary']['score_reason']}
    # Leak Analysis
    leak_products_list = leak_score_data['leak_products']
    leak_df = df[df['title'].isin(leak_products_list)]

    leak_df.rename(columns={
    'title': 'product',
    'macro_category': 'macro category',
    'master_category': 'master category'
    }, inplace=True)

    
    leak_df = leak_df[['product', 'amount', 'master category', 'macro category', 'type', 'timestamp']]
    leak_products_count = leak_df['product'].value_counts()
    leak_products_count_dict = leak_products_count.to_dict()
    leak_products_amount = leak_df.groupby('product')['amount'].sum().reset_index()
    
    # Budget & Risk
    df_budgets = df_budgets[['category', 'limit_amount']]
    budget = dict(zip(df_budgets['category'], df_budgets['limit_amount']))
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    needs_spending = int(df[df['macro_category'] == 'NEEDS']['amount'].sum())
    wants_spending = int(df[df['macro_category'] == 'WANTS']['amount'].sum())
    others_spending = int(df[df['macro_category'] == 'OTHERS']['amount'].sum())
    df_expense = df[df['type'] == 'EXPENSE']
    daily_spending = df_expense.groupby(df_expense['timestamp'].dt.date)['amount'].sum().reset_index()
    # Recent Transactions
    weekly_spending = df.groupby(pd.Grouper(key='timestamp', freq='W'))['amount'].sum().reset_index()
    # Get Month
    date = data['start_date']
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
    month_year = date_obj.strftime('%B %Y')
    # Weekly Rewind
    weekly_summary = get_weekly_summary(df)
    weekly_summary_percentages = get_weekly_summary_percentages(weekly_summary)
    return_value = {
        # Financial Score
        'financial_score': financial_score,
        # Metrics
        'metrics': metrics,
        # Leaks
        'leak_df': leak_df,
        'leak_products': leak_products_list,
        'leak_products_count_dicts': leak_products_count_dict,
        'leak_amount': leak_products_amount,
        # Budget & Risk
        'budget': budget,
        'needs_spending': needs_spending,
        'wants_spending': wants_spending,
        'others_spending': others_spending,
        'daily_spending': daily_spending,
        'weekly_spending': weekly_spending,
        # Weekly Rewind
        'weekly_summary': weekly_summary,
        'weekly_summary_percentages': weekly_summary_percentages,
        # Miscellanious
        'current_month_year': month_year,
        'spending_data': df_expense
    }
    
    return return_value