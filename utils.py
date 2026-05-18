import json
import os
import pandas as pd

def load_data():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, 'data', 'mockDashboardAnalysis.json')
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # If it's a raw JSON (has transactions but no financial_score), process it
            if "transactions" in data and "financial_score" not in data:
                return process_raw_data(data)
            return data
    except Exception as e:
        return None

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

def process_raw_data(raw_data):
    """
    Transforms raw transaction data into the expected dashboard format.
    This acts as our Data Wrangling & Feature Engineering pipeline.
    """
    transactions = raw_data.get("transactions", [])
    budgets = raw_data.get("budgets", [])
    
    if not transactions:
        return raw_data
        
    df = pd.DataFrame(transactions)
    df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # 1. Financial Score & Metrics
    income = df[df['type'] == 'INCOME']['total_amount'].sum()
    expense = df[df['type'] == 'EXPENSE']['total_amount'].sum()
    net_cashflow = income - expense
    savings_rate = (net_cashflow / income) if income > 0 else 0
    
    expense_df = df[df['type'] == 'EXPENSE']
    needs_total = expense_df[expense_df['category'] == 'NEEDS']['total_amount'].sum()
    wants_total = expense_df[expense_df['category'] == 'WANTS']['total_amount'].sum()
    others_total = expense_df[expense_df['category'] == 'OTHERS']['total_amount'].sum()
    
    needs_ratio = (needs_total / income) if income > 0 else 0
    wants_ratio = (wants_total / income) if income > 0 else 0
    others_ratio = (others_total / income) if income > 0 else 0
    
    score = min(100, max(0, int(savings_rate * 100)))
    if score >= 80:
        score_cat = "Excellent"
        reason = "Good job! You saved a large portion of your income."
    elif score >= 60:
        score_cat = "Good"
        reason = "Your finances are healthy, but watch your Wants spending."
    else:
        score_cat = "Needs Improvement"
        reason = "Warning! Your expenses are too high compared to your income."

    # 2. Leak Detection
    leaks = []
    wants_others_df = expense_df[expense_df['category'].isin(['WANTS', 'OTHERS'])]
    
    if not wants_others_df.empty:
        leak_grouped = wants_others_df.groupby('description').agg(
            frequency=('id', 'count'),
            total_spending=('total_amount', 'sum'),
            category=('category', 'first')
        ).reset_index()
        
        # Rule: item bought > 2 times is a potential leak
        for _, row in leak_grouped.iterrows():
            is_leak = int(row['frequency'] > 2)
            leaks.append({
                "description": row['description'],
                "category": row['category'],
                "frequency": int(row['frequency']),
                "total_spending": float(row['total_spending']),
                "rule_leak_type": "HIGH_FREQUENCY" if is_leak else "NORMAL",
                "is_final_potential_leak": is_leak
            })
            
    leaks = sorted(leaks, key=lambda x: x['total_spending'], reverse=True)
    potential_leaks = [l for l in leaks if l['is_final_potential_leak'] == 1]
    
    top_leak_item = potential_leaks[0]['description'] if potential_leaks else "-"
    top_leak_spending = potential_leaks[0]['total_spending'] if potential_leaks else 0
    
    # 3. Budget Summary
    budget_summary = []
    overbudget_count = 0
    total_limit = 0
    
    for b in budgets:
        cat = b.get('category')
        limit = b.get('limit_amount', 0)
        actual = expense_df[expense_df['category'] == cat]['total_amount'].sum()
        ratio = (actual / limit) if limit > 0 else 0
        risk = "High Risk" if ratio > 0.9 else ("Medium Risk" if ratio > 0.7 else "Low Risk")
        if ratio > 1:
            overbudget_count += 1
            
        total_limit += limit
        budget_summary.append({
            "category": cat,
            "limit_amount": limit,
            "actual_spending": actual,
            "remaining_budget": max(0, limit - actual),
            "budget_used_ratio": ratio,
            "risk_level": risk
        })
        
    budget_used_ratio_total = (expense / total_limit) if total_limit > 0 else 0

    # 4. Daily Spending
    daily_spending = []
    if not expense_df.empty:
        expense_df['date_only'] = expense_df['transaction_date'].dt.strftime('%Y-%m-%d')
        daily_grouped = expense_df.groupby('date_only')['total_amount'].sum().reset_index()
        for _, row in daily_grouped.iterrows():
            daily_spending.append({"date": row['date_only'], "amount": float(row['total_amount'])})

    # 5. Recent Transactions
    df_sorted = df.sort_values(by='transaction_date', ascending=False).head(10)
    df_sorted['transaction_date'] = df_sorted['transaction_date'].dt.strftime('%Y-%m-%d %H:%M')
    recent_transactions = df_sorted[['transaction_date', 'description', 'category', 'total_amount', 'type']].to_dict('records')

    # Build final transformed dict
    transformed_data = {
        "month_period": raw_data.get("month_period", ""),
        "financial_score": {
            "financial_score": score,
            "score_category": score_cat,
            "score_reason": reason,
            "metrics": {
                "total_income": income,
                "total_expense": expense,
                "net_cashflow": net_cashflow,
                "savings_rate": savings_rate,
                "needs_ratio": needs_ratio,
                "wants_ratio": wants_ratio,
                "others_ratio": others_ratio,
                "budget_used_ratio_total": budget_used_ratio_total,
                "overbudget_category_count": overbudget_count
            }
        },
        "leak_detection": {
            "summary": {
                "final_potential_leak_count": len(potential_leaks),
                "top_leak_item": top_leak_item,
                "top_leak_total_spending": top_leak_spending
            },
            "leaks": leaks
        },
        "budget_summary": budget_summary,
        "spending_breakdown": [
            {"category": "NEEDS", "amount": needs_total},
            {"category": "WANTS", "amount": wants_total},
            {"category": "OTHERS", "amount": others_total}
        ],
        "daily_spending": daily_spending,
        "recent_transactions": recent_transactions,
        "weekly_rewind": {
            "weekly_income": income / 4,
            "weekly_expense": expense / 4,
            "weekly_net_cashflow": (income - expense) / 4,
            "top_category": "WANTS" if wants_total > needs_total else "NEEDS",
            "top_category_spending": max(wants_total, needs_total) / 4,
            "top_leak_item": top_leak_item,
            "weekly_insight": "AI Rewind analysis derived from raw transactions."
        }
    }

    return transformed_data
