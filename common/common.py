# common.py - Shared reusable code for Bitcoin Income Suite V2
import os
import json
import csv
import sqlite3
import requests
from datetime import datetime
from sklearn.tree import DecisionTreeClassifier  # For simple ML in AI nudges (adjust as needed)

# Constants for Bitcoin CAGR and Diminishing Returns Projection (Fixed, no user sliders)
BITCOIN_CURRENT_PRICE = 118000  # USD as of July 2025; fallback for API failures
BITCOIN_HISTORICAL_CAGR = 0.822  # r0 ≈82.2% (10-year historical)
DECAY_FACTOR = 0.8525  # d solved to reach exactly $10M in 2045

def get_bitcoin_growth_rate(year_from_2025):
    """Returns rt for year t (t=1 for 2026, etc.)"""
    t = year_from_2025 + 1  # Adjust for t starting at 1
    rt = BITCOIN_HISTORICAL_CAGR * (DECAY_FACTOR ** (t - 1))
    return rt

def project_bitcoin_price(years_ahead, start_price=BITCOIN_CURRENT_PRICE):
    """Projects Bitcoin price over years_ahead from 2025, reaching ~$10M by 2045."""
    p = start_price
    for t in range(1, years_ahead + 1):
        rt = get_bitcoin_growth_rate(t - 1)
        p *= (1 + rt)
    return p

# Inflation/Debasement Rate (For TRE erosion sims, Opportunity Cost; compounded annually)
CPI_INFLATION_AVG = 0.027
M2_DEBASEMENT_AVG = 0.065  # M2 from ~$12.1T in 2015 to ~$22T in 2025
TOTAL_DEBASEMENT_RATE = CPI_INFLATION_AVG + M2_DEBASEMENT_AVG  # 9.2%

def project_inflation_erosion(start_value, years, rate=TOTAL_DEBASEMENT_RATE):
    """Projects value erosion over years at compounded rate."""
    return start_value * ((1 + rate) ** years)

# Comparison Asset Performances (For Opportunity Cost, TRE; fixed, 2010-2025 averages)
GOLD_CAGR = 0.0704  # ~7.04% (e.g., $1,200 in 2010 to ~$3,300 in 2025)
SP500_CAGR = 0.138  # ~13.8% (S&P 500 historical CAGR)
SAVINGS_RATE_AVG = 0.003  # ~0.3% (US savings rate, FDIC/Forbes)

def project_asset_growth(start_value, years, asset_cagr):
    """Projects growth for comparison assets at fixed CAGR or Bitcoin projection."""
    if asset_cagr == 'bitcoin':
        return project_bitcoin_price(years, start_value)  # Delegate to Bitcoin-specific projection
    return start_value * ((1 + asset_cagr) ** years)

# DGI Calculation
def calculate_dgi(base, sweep_amount, spend_amount, factor=1.0):
    """Compute DGI score: base + (sweep_amount / spend_amount) * factor, normalized 0-100."""
    score = base + (sweep_amount / spend_amount) * factor
    return min(max(score, 0), 100)  # Normalize

# Bitcoin Sweep Logic
def bitcoin_sweep_logic(income, allocation_pct=0.3):
    """Calculate sats swept based on income and allocation percentage."""
    swept_amount = income * allocation_pct
    sats_swept = swept_amount / BITCOIN_CURRENT_PRICE * 100000000  # Convert to sats (1 BTC = 100M sats)
    return sats_swept

# Gamification Utils (using streamlit-badges or simple text)
def award_badge(level):
    """Generate badge based on DGI level (e.g., 'Time Protector' for DGI >60)."""
    if level > 80:
        return "Time Protector Badge Earned!"
    elif level > 60:
        return "Sweep Starter Badge Earned!"
    else:
        return "Debasement Learner Badge Earned!"

# Backtesting Logic
def backtest_bitcoin_sweep(stock_income, years):
    """Simulate historical Bitcoin sweeps vs. fiat/S&P for time reclamation visuals."""
    bitcoin_value = project_bitcoin_price(years, stock_income)
    fiat_value = project_inflation_erosion(stock_income, years)
    sp_value = project_asset_growth(stock_income, years, SP500_CAGR)
    return {
        "bitcoin_value": bitcoin_value,
        "fiat_value": fiat_value,
        "sp_value": sp_value
    }

# AI Nudge Logic
def generate_nudge(user_level, dgi_score, user_data):
    """Generate tiered nudge based on user level and DGI score using simple ML or rules."""
    # Simple rule-based for fallback; can integrate ML (e.g., DecisionTreeClassifier)
    if user_level == "Beginner":
        return "Learn why Bitcoin beats 9.2% inflation—try a $50 sweep to reclaim time!"
    elif user_level == "Intermediate":
        return f"Your DGI is {dgi_score}—sweep 20% dividends for 100 hours saved!"
    else:  # Advanced
        return "Optimize MSTR premium sweep with RSI trends for max sats and time freedom!"

# Export/Import Standards
def export_data(data, format='json', filename='export.json'):
    """Export data to JSON or CSV."""
    if format == 'json':
        with open(filename, 'w') as f:
            json.dump(data, f)
    elif format == 'csv':
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(data.keys())
            writer.writerow(data.values())

# Real-Time Data Handling
import streamlit as st  # Ensure this is at the top

def fetch_stock_data(ticker, api_key=os.getenv('ALPHA_VANTAGE_API_KEY')):
    """Fetch live RSI for stock/MSTR from Alpha Vantage."""
    if not api_key:
        return {'rsi': 50, 'premium_yield': 0.02}
    url = f"https://www.alphavantage.co/query?function=RSI&symbol={ticker}&interval=5min&time_period=14&series_type=close&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        rsi_data = data.get('Technical Analysis: RSI', {})
        if rsi_data:
            latest_rsi = None
            for date, values in rsi_data.items():
                try:
                    rsi_value = float(values.get('RSI', '50'))
                    if latest_rsi is None or date > latest_rsi_date:
                        latest_rsi = rsi_value
                        latest_rsi_date = date
                except (ValueError, TypeError):
                    continue
            latest_rsi = latest_rsi or 50
        else:
            latest_rsi = 50
        # Mock premium yield based on RSI trend (e.g., RSI / 1000 for 5-6% range)
        premium_yield = latest_rsi / 1000  # No cap for variability
        return {'rsi': latest_rsi, 'premium_yield': premium_yield}
    else:
        return {'rsi': 50, 'premium_yield': 0.02}  # Fallback

def fetch_bitcoin_price(api_key=os.getenv('COINGECKO_API_KEY')):
    """Fetch live Bitcoin price from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['bitcoin']['usd']
    else:
        return BITCOIN_CURRENT_PRICE  # Fallback

def get_fallback_data(asset_type):
    """Return hardcoded averages for uptime."""
    if asset_type == 'stock':
        return {"premium_yield": 0.02, "rsi": 50, "delta": 0.3}
    return BITCOIN_CURRENT_PRICE  # For Bitcoin

# Societal Impact Metrics Aggregation
def aggregate_societal_metrics(user_data_list):
    """Aggregate anonymized hours reclaimed across users."""
    total_hours = 0
    for user_data in user_data_list:
        # Example calculation: hours = (sweep_amount / hourly_wage) * growth_factor
        total_hours += user_data['sweep_amount'] / user_data['hourly_wage'] * 2  # Simplified
    return total_hours

# Additional utilities as needed for X exports, etc.
def export_to_x(milestone_data, user_id):
    """Export milestone to X (using tweepy; assume API setup)."""
    # Placeholder: print("Posted to X: " + milestone_data['message'])
    return "Export successful"