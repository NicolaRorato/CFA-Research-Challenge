# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 18:15:33 2021

@author: Nicola
"""

import financialmodelingprep_data_import as statements
import alphavantage_data_import as alphav
import financialEvaluation as val
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

api_keys = ['YOUR_API_KEY', 'YOUR_API_KEY'] # financialmodelingprep, alphavantage
ticker = 'HLI'

if __name__ == "__main__":
    if os.path.exists('pd_statements/income_statement') and os.path.exists('pd_statements/balance_sheet') and os.path.exists('pd_statements/dividends_history'):
        income_statement = pd.read_pickle('pd_statements/income_statement')
        balance_sheet = pd.read_pickle('pd_statements/balance_sheet')
        dividends = pd.read_pickle('pd_statements/dividends_history')
    
    else:        
        income_statement = statements.income_statement(ticker, api_keys[0])
        balance_sheet = statements.balance_sheet(ticker, api_keys[0])
        dividends = statements.dividends_history(ticker, api_keys[0])
        print('DB Queried')
    
        try:
            os.makedirs('pd_statements/')
        except:
            pass
        income_statement.to_pickle('pd_statements/income_statement')
        balance_sheet.to_pickle('pd_statements/balance_sheet')
        dividends.to_pickle('pd_statements/dividends_history')
    
    annual_dividends = dividends[['adjDividend', 'dividend']].groupby(by=[dividends.index.year], sort=False).sum() # US based firms pay quarterly dividends. We get the annual dividend summing the 4 most recent
    annual_dividends.index = pd.to_datetime(annual_dividends.index, format='%Y') + pd.offsets.MonthBegin(2) + pd.offsets.Day(30) # offset dates to allow operations with financial statements dataframes
    ## finalDividend = initialDividend * (1 + annualDividendGrowth)**years
    annual_dividend_growth = (annual_dividends.iloc[0]['adjDividend'] / annual_dividends.iloc[5]['adjDividend'])**(1/6) - 1
    
    ## Assumptions
    ## 3-months bills are often taken as reference risk free rates
    yields_3m_bills = alphav.get_treasury_yields(api_keys[1], 'Daily', '3month') # percentages
    rf = 1.42/100 # temporary - Longstaff
    beta = 0.95 # temporary - https://smf.business.uconn.edu/wp-content/uploads/sites/818/2020/02/HLI-One-Pager-v6.pdf
    mpremium = 5.5/100 # https://www.duffandphelps.com/-/media/assets/pdfs/publications/articles/dp-erp-rf-table-2021.pdf , bibliography
    #mpremium = 4.38/100 # https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3879109, bibliography
    sustainable_growth_rate = 3/100 # temporary - check avg industry
    cost_of_capital = val.capm(rf, beta, mpremium)
    
    ### Gordon Growth Model
    ## roe = net income / avg shareholders equity
    net_income = income_statement['netIncome']
    avg_shareholders_equity = 0.5*balance_sheet['totalStockholdersEquity'] + 0.5*balance_sheet['totalStockholdersEquity'].shift(-1)
    accounting_ratios = pd.DataFrame(net_income/avg_shareholders_equity, columns=['ROE'])
    
    ## g = ROE(1 - payout ratio)
    accounting_ratios['Payout Ratio'] = annual_dividends['adjDividend'][:len(income_statement['eps'])] / income_statement['eps']
    accounting_ratios['g - Sustainable Growth Rate'] = accounting_ratios['ROE'] * (1 - accounting_ratios['Payout Ratio'])
    # we get a very high g from HLI statements. It is therefore wiser to get a reference g from the industry and estimate a meaningful payout ratio
    
    ## During a recession (temporary) the values of net income and other accounting
    ## measure may be severily affected and not represent a meaningful
    ## base of estimation for future years earnings
    ## therefore it is reasonable to exclude the year and consider
    ## an average of the ROE in previous 5-10 years
    ##
    ## To forecast next period earnings:
    ## E = book value of equity * normalized ROE
    ## We can now estimate the dividend payout ratio:
    ## payout ratio = 1 - g / normalized ROE
    ## And using the gordon growth model:
    ## Intrinsic Value of Equity = E * payout ratio / (cost of equity - g)
    ## Our estimations are ROE and cost of equity ->
    ## we should check value estimation when these parameters change
    
    normalized_roe = accounting_ratios['ROE'][1:-1].mean() # excluding last year
    
    scenarios = ['Case1', 'Case2', 'Case3']
    intrinsic_value_table = pd.DataFrame(columns=['Next Period EPS', 'ROE', 'Payout Ratio', 'Cost of Equity', 'Estimated Value'], index=scenarios)   
    
    for i in range(len(scenarios)):
        next_period_earnings = balance_sheet['totalStockholdersEquity'][0]/income_statement.iloc[0]['weightedAverageShsOut'] * normalized_roe
        estimated_payout_ratio = 1 - sustainable_growth_rate / accounting_ratios['ROE'][1:-1].mean()
        intrinsic_value = next_period_earnings*estimated_payout_ratio / (cost_of_capital - sustainable_growth_rate)
        
        intrinsic_value_table.loc[scenarios[i]] = [next_period_earnings, normalized_roe, estimated_payout_ratio, cost_of_capital, intrinsic_value]
        
        cost_of_capital += 0.01
        normalized_roe -= 0.05
    #intrinsic_value = val.gordon_growth(annual_dividends.iloc[0]['adjDividend'], cost_of_capital, sustainable_growth_rate, annual_dividend_growth, 3)
    
    
    
    current_eps = income_statement['eps'][0]
    current_retained_earnings = balance_sheet['retainedEarnings'][0]
    
    
    
    ### Multiplier Models
    ## primary competitors vary by product and industry expertise and would include the following:
    ## for our CF practice, Jefferies LLC,Lazard Ltd, Moelis & Company, N M Rothschild & Sons Limited, Piper Sandler Companies, Robert W. Baird & Co. Incorporated, StifelFinancial Corp., William Blair & Company, L.L.C., and the bulge-bracket investment banking firms
    ## for our FR practice, Evercore Partners,Lazard Ltd, Moelis & Company, N M Rothschild & Sons Limited and PJT Partners
    ## for our FVA practice, Duff & Phelps Corp., the “bigfour” accounting firms, and various global financial advisory firms
    
    latest_price = float(alphav.get_live_updates(api_keys[1], ticker).loc['price'])
    price_to_book = latest_price / balance_sheet['totalStockholdersEquity'][0] * income_statement.iloc[0]['weightedAverageShsOut']
    
    competitors = ['HLI', 'JEF', 'LAZ', 'MC', 'PIPR', 'SF', 'JPM', 'GS', 'EVR', 'DPG']
    
    pb_table = pd.DataFrame(columns=['Company', 'P/B', 'ROE'])
    pb_table.set_index('Company', inplace=True)
    pb_table.loc[ticker] = [price_to_book, accounting_ratios['ROE'][0]]
    #pd.DataFrame([{ticker: price_to_book}])
    for competitor in competitors[1:]:
        if os.path.exists('pd_statements/' + 'bsh' + competitor) and os.path.exists('pd_statements/' + 'ist' + competitor):
            ist = pd.read_pickle('pd_statements/' + 'ist' + competitor)
            balance_sheet = pd.read_pickle('pd_statements/' + 'bsh' + competitor)
    
        else:        
            ist = statements.income_statement(competitor, api_keys[0])
            bsh = statements.balance_sheet(competitor, api_keys[0])
            ist.to_pickle('pd_statements/' + 'bsh' + competitor)
            bsh.to_pickle('pd_statements/' + 'bsh' + competitor)
        
        p = float(alphav.get_live_updates(api_keys[1], competitor).loc['price'])
        
        roe =  ist['netIncome']/(0.5*bsh['totalStockholdersEquity'] + 0.5*bsh['totalStockholdersEquity'].shift(-1))
        pb = p / bsh['totalStockholdersEquity'][0] * ist.iloc[0]['weightedAverageShsOut']
        
        pb_table.loc[competitor] = [pb, roe[0]]
    
    plt.plot(pb_table['ROE'], pb_table['P/B'], 'o', color='grey')
    plt.xlabel('ROE')
    plt.ylabel('P/B')
    plt.title("Price to Book Ratios vs Return on Equity: HLI and competitors",fontsize=12)
    for i, label in enumerate(competitors):
        plt.annotate(label, (pb_table['ROE'][i], pb_table['P/B'][i]), xytext=(pb_table['ROE'][i]-0.05, pb_table['P/B'][i]+.03), fontsize=8)
    b1, b0 = np.polyfit(pb_table['ROE'], pb_table['P/B'], 1)
    plt.plot(pb_table['ROE'], b1*pb_table['ROE']+b0, color='red')
    plt.figure(figsize=(1,1), dpi=100)
    plt.show()
