import json
import os

def load_data():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, 'data', 'mockDashboardAnalysis.json')
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
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
