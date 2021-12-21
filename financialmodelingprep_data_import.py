# -*- coding: utf-8 -*-
"""
Created on Sun Nov 28 23:02:08 2021

@author: Nicola
"""

import pandas as pd
import requests
import json


def balance_sheet(ticker, api_key):
    '''Balance Sheet Statement'''
    api_url = f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?limit=120&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df

def income_statement(ticker, api_key):
    '''Comprehensive Income Statement'''
    api_url = f'https://financialmodelingprep.com/api/v3/income-statement/{ticker}?&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df

def dividends_history(ticker, api_key):
    '''Company dividends History'''
    api_url = f'https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{ticker}?apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df['historical'])
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    df['dividendIncrease'] = df['adjDividend'] / df['adjDividend'].shift(-1)
    return df

def financialratios(ticker, api_key):
    '''Financial Ratios'''
    api_url = f'https://financialmodelingprep.com/api/v3/financial-ratios/{ticker}?apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df['ratios'])
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    valuation_ratios = pd.json_normalize(df['investmentValuationRatios'])
    valuation_ratios.set_index(df.index, inplace=True)
    profitability_indicator_ratios = pd.json_normalize(df['profitabilityIndicatorRatios'])
    profitability_indicator_ratios.set_index(df.index, inplace=True)
    operating_performance_ratios = pd.json_normalize(df['operatingPerformanceRatios'])
    operating_performance_ratios.set_index(df.index, inplace=True)
    liquidity_ratios = pd.json_normalize(df['liquidityMeasurementRatios'])
    liquidity_ratios.set_index(df.index, inplace=True)
    debt_ratios = pd.json_normalize(df['debtRatios'])
    debt_ratios.set_index(df.index, inplace=True)
    cash_flow_ratios = pd.json_normalize(df['cashFlowIndicatorRatios'])
    cash_flow_ratios.set_index(df.index, inplace=True)
    return valuation_ratios, profitability_indicator_ratios, operating_performance_ratios, liquidity_ratios, debt_ratios, cash_flow_ratios

def institutional_holders(ticker, api_key, date): # only available to premium users
    '''Institutional Holders List - PREMIUM API FEATURE'''
    # api_url = f'https://financialmodelingprep.com/api/v3/institutional-holder/{ticker}?apikey={api_key}'
    api_url = f'https://financialmodelingprep.com/api/v4/institutional-ownership/institutional-holders/symbol-ownership?date={date}&symbol={ticker}&page=0&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df

def historical_daily_price(ticker, api_key):
    '''Historical Stock Prices'''
    api_url = f'https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df

def insider_trading(ticker, api_key):
    '''Insiders Stock Trading - PREMIUM API FEATURE'''
    api_url = f'https://financialmodelingprep.com/api/v4/insider-trading?symbol={ticker}&limit=100&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df

def analyst_estimates(ticker, api_key):
    '''Analayst forecasts - PREMIUM API FEATURE'''
    api_url = f'https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}?limit=30&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df

def stock_grading(ticker, api_key):
    '''Analysts Company Grading - PREMIUM API FEATURE'''
    api_url = f'https://financialmodelingprep.com/api/v3/grade/{ticker}?limit=500&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df)
    df.set_index('gradingCompany', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df

def social_sentiment(ticker, api_key):
    '''Social Media Sentiment - PREMIUM API FEATURE'''
    api_url = f'https://financialmodelingprep.com/api/v4/historical/social-sentiment?symbol={ticker}&limit=100&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df)
    df.set_index('country', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df

def markets_risk_premium(api_key):
    '''Global Markets Equity Risk Premiums - PREMIUM API FEATURE'''
    api_url = f'https://financialmodelingprep.com/api/v4/market_risk_premium?apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df)
    df.set_index('country', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df

def treasury_rates(api_key):
    '''Treasury Yields - PREMIUM API FEATURE'''
    end_date = str(pd.to_datetime('today'))[:10]
    initial_date = str(pd.to_datetime('today').normalize()-pd.DateOffset(months=3))[:10] # maximum period allowed is 3 months
    api_url = f'https://financialmodelingprep.com/api/v4/treasury?from={initial_date}&to={end_date}&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)