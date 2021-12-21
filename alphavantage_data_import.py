# -*- coding: utf-8 -*-
"""
Created on Sun Nov 21 10:37:05 2021

@author: Nicola
"""

import pandas as pd
import numpy as np
import requests

def get_live_updates(api_key, symbol):
    api_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    attributes = {'attributes':['symbol', 'open', 'high', 'low', 'price', 'volume', 'latest trading day', 'previous close', 'change', 'change percent']}
    attributes_df = pd.DataFrame(attributes)
    values = []
    for i in list(raw_df['Global Quote']):
        values.append(raw_df['Global Quote'][i])
    values_df = pd.DataFrame(values).rename(columns = {0:'values'})
    frames = [attributes_df, values_df]
    df = pd.concat(frames, axis = 1, join = 'inner').set_index('attributes')
    return df

def get_intraday_data(api_key, symbol, interval):
    '''Pull Intraday Data'''
    
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df[f'Time Series ({interval})']).T
    df = df.rename(columns = {'1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. volume': 'volume'})
    for i in df.columns:
        df[i] = df[i].astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.iloc[::-1]
    return df

def get_historical_data(api_key, symbol, start_date = None):
    '''Pull Historical Data'''
    
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}&outputsize=full'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df['Time Series (Daily)']).T
    df = df.rename(columns = {'1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. adjusted close': 'adj close', '6. volume': 'volume'})
    for i in df.columns:
        df[i] = df[i].astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.iloc[::-1].drop(['7. dividend amount', '8. split coefficient'], axis = 1)
    if start_date:
        df = df[df.index >= start_date]
    return df

def get_daily_exchange_rates(api_key, symbol, base_currency):
    '''Pull Daily Exchange Rates'''
    cryptoccy_list = open('cryptoccy_list.txt').read().splitlines()
    
    if symbol in cryptoccy_list:
        api_url = f'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market={base_currency}&apikey={api_key}&outputsize=full'
        interval = '(Digital Currency Daily)'
    else:
        api_url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={base_currency}&to_symbol={symbol}&apikey={api_key}&outputsize=full'
        interval = 'FX (Daily)'
    
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df[f'Time Series {interval}']).T
    df = df.rename(columns = lambda x: x.split(' ', 1)[1])
    for i in df.columns:
        df[i] = df[i].astype(float)
    df.index = pd.to_datetime(df.index)
    return df

def get_treasury_yields(api_key, interval, maturity):
    '''Pull Treasury Yields'''
    
    api_url = f'https://www.alphavantage.co/query?function=TREASURY_YIELD&interval={interval}&maturity={maturity}&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    #print(raw_df['data'])
    df = pd.DataFrame(raw_df['data'])
    for i in df.columns[1:]:
        df[i] = df[i].astype(float)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df

def get_financial_statements(api_key, function_code, symbol):
    '''Get Financial Statements and Company Overview'''
    switcher = {0: 'INCOME_STATEMENT', 1: 'BALANCE_SHEET', 2: 'CASH_FLOW', 3: 'OVERVIEW'}
    function = switcher.get(function_code)
    api_url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    #print(raw_df)
    if function_code in list(switcher.keys())[:3]:
        df = pd.DataFrame(raw_df['annualReports'])
    elif function_code == 3:
        df = pd.DataFrame([raw_df])     
    return df