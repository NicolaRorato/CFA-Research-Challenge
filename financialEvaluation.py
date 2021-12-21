# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 19:54:41 2021

@author: Nicola
"""

def capm(rf, beta, mpremium):
    '''CAPM - Capital Asset Pricing Model'''
    
    return rf + beta*mpremium


def excess_return(net_income, cost_of_equity, end_period_equity, expected_growth_rate):
    return (net_income - end_period_equity * cost_of_equity) / (cost_of_equity - expected_growth_rate)


def gordon_growth(current_dividend, cost_of_capital, stable_growth_rate, unstable_growth_rate=0, unstable_growth_period=0):
    '''Gordon Growth Model
    \nPass additional arguments unstable_growth_rate, unstable_growth_period to use two-stage dividend discount model'''
    
    dividend = current_dividend
    pv = 0
    t = -1
    
    if unstable_growth_period == 0:
        n=1
    else:
        n=2
        for t in range(1, unstable_growth_period+1):
            dividend *= (1+unstable_growth_rate)**t
            pv += dividend / (1+cost_of_capital)**t   
        pv += dividend*(1+stable_growth_rate)**1 / (1+cost_of_capital)**(t+1) # add first stable dividend discounted to present
        
    gg = dividend*(1+stable_growth_rate)**n / (cost_of_capital - stable_growth_rate) # gordon growth value estimation
    
    return pv + gg / (1+cost_of_capital)**(t+1)


def net_income_forecast(initial_period_equity, equity_growth_rate, roe):
    return initial_period_equity * equity_growth_rate * roe

def sustainable_growth_rate(roe, dividend_payout_ratio):
    return roe * (1 - dividend_payout_ratio)

def value_of_equity(current_period_equity, pv_excess_returns5y, pv_terminal_excess_returns):
    return current_period_equity + pv_excess_returns5y + pv_terminal_excess_returns