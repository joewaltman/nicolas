# -*- coding: utf-8 -*-
"""
Created on Tue May 29 10:44:47 2018

@author: Nicolas
"""

import requests 
import pandas as pd 

def get_ohlcv(token):
    
    prices = []
    
    response = requests.get('https://api.bitfinex.com/v2/candles/trade:1D:t{}/hist?limit=1000'.format(token))
    data = response.json()
        
    for item in data:
        date = item[0]
        open_ = item[1]
        close = item[2]
        high = item[3]
        low = item[4]
        volume = item[5]
        one_item_list = {"Date": date,"Open":open_,"High":high,"Low":low,"Close":close,"Volume":volume}
        prices.append(one_item_list)
    

    df = pd.DataFrame(prices, columns=["Date","Open", "High", "Low", "Close","Volume"])
    df["Date"] = pd.to_datetime(df["Date"], unit = 'ms')
    df = df.set_index("Date")
    df.sort_index(inplace=True)
    #btc_data = btc_data.drop(["Date"],axis=1)
    df.to_csv("{}.csv".format(token))            
    
    return df 

bch = get_ohlcv("BCHUSD")
eos = get_ohlcv("EOSUSD")
btc_usd = get_ohlcv("BTCUSD")


def rlz(df):
    
    windows = [200,100,50]
    data = []
    for window in windows:
        big_df = df[:window]
        max_value = big_df["High"].max()
        min_value = big_df["Low"].min()
        max_value_date = big_df["High"].idxmax()
        min_value_date = big_df["Low"].idxmin()
        max_value_date_dt = pd.to_datetime(max_value_date,unit='D')
        min_value_date_dt = pd.to_datetime(min_value_date, unit = 'D')
        print("max value for window %s: " % (window), max_value)
        print("min_value_for window %s: " % (window), min_value)
    
        for i in range(window - 1,-1,-1):
        
            big_df.loc[big_df.index[i],"rlz_%s_low" % str(window)] = min_value   #,min_value_date 
            big_df.loc[big_df.index[i],'rlz_%s_low_value_date' % str(window)] = min_value_date_dt
            big_df.loc[big_df.index[i],"rlz_%s_high" % str(window)] = max_value # , max_value_date
            big_df.loc[big_df.index[i],'rlz_%s_max_value_date' % str(window)] = max_value_date_dt         
    
            if max_value_date > min_value_date:
        
                big_df.loc[big_df.index[i], "rlz_%s_type" % str(window)] = 'bull'
                big_df.loc[big_df.index[i], "rlz_%s_fib" % str(window)] = (big_df["Close"][i] - min_value) / (max_value - min_value)
        
            if min_value_date > max_value_date:
        
                big_df.loc[big_df.index[i],"rlz_%s_type" % str(window)] = 'bear'
                big_df.loc[big_df.index[i], "rlz_%s_fib" % str(window)] = (max_value - big_df["Close"][i]) / (max_value - min_value)
    
        
        data.append(big_df)
    return data
    
ohlcv_rlz = rlz(btc_usd)

def combine_data(data):

    df = pd.concat([data[0],data[1],data[2]],axis=1)
    
    return df 

final_output = combine_data(ohlcv_rlz)
final_output.to_exel('path.xlsx')









