# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 14:38:30 2018

@author: Nicolas
"""

import requests
import pandas as pd


tokens = ['2GIVE','ANT','ATB','AVT','B3','BAT','BAY','BCD','BCH','BITB','BITUSD','BNT','BQ','BTC','BTG','BTS']

def get_data(tokens):
    
    item_list = []
    for token in tokens:
        response = requests.get('https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={}&market=USD&apikey=3TZQQTZPAV1IN50Q'.format(token))
        data = response.json()
        ohlc = data['Time Series (Digital Currency Daily)']
        for key,value in ohlc.items():
            token = data["Meta Data"]['2. Digital Currency Code']
            date = key
            open_ = value['1a. open (USD)']
            high = value['2a. high (USD)']
            low = value['3b. low (USD)']
            close = value['4a. close (USD)'] 
            volume = value['5. volume']
            one_item_list = {"token":token,"date":date,"open":open_, "high":high, "low":low, "close":close,"volume":volume}
            item_list.append(one_item_list)
        print("Finish to process data for token %s" % token)
    
    tokens = pd.DataFrame(item_list,columns=["token","date","open","high","low","close","volume"]) # .pivot(index="date",columns="symbol",values="close"))
    # Make a multindex dataframe with the token as the level 0 and date as the level 1
    all_tokens = tokens.set_index(["token","date"])
    # Sort index by date 
    all_tokens = all_tokens.sort_index(axis=1)
    
    return all_tokens 
            
df = get_data(tokens)  #df is the dataframe that contain the ohlcv values for each index. It is a multindex dataframe with the tokens as primary level and the date as second level      


def macd(df):
    # get the index of the level 0 in the df dataframe
    tokens = df.index.levels[0]
    # create an empty dataframe called macds to fill the columns with the macd_signal values in line 58
    macds = pd.DataFrame(columns=[tokens],index=df.index.levels[1])
    # Loop over each token to calculate macd
    for token in tokens:
        close = df.loc[token]["close"]# retrieve only values related to the token in the df dataframe
        close = close.sort_index()
        ema_30 = close.ewm(span=30, min_periods=30+1).mean()
        ema_9 = close.ewm(span=9,  min_periods=9+1).mean()
        
        macd = ema_9 - ema_30
        macd_signal = macd.ewm(span=9,min_periods=9+1).mean()
        histo_macd = macd - macd_signal 
        histo_macd_df = pd.DataFrame(histo_macd.values,index=histo_macd.index, columns=[token]) # make a dataframe 
        
        macds[token] = histo_macd_df
        
        print("calculating macd for token %s" % token)
    macds = macds.dropna() # eliminate null values 
    return macds
histo_macd_values = macd(df) # final_data is a dataframe with the macd histogram values. If the value is positive could be interpreted as a buy signal 

def RSI(df,period=14):
    #df is the result of the get_data function
    closes = df["close"] # retrieve only closes values for all the tokens
    closes = closes.unstack(level=0) # change the format of the closes dataframe in order to have the tokens in the columns and the date as the unique index
    all_closes = closes.apply(pd.to_numeric, errors = 'ignore') # the all_closes dataframe is a dataframe with numeric values instead of object type of the closes dataframe
    delta = all_closes.diff() # make the difference between the prices between two consecutive days
        
    up, down = delta.copy(), delta.copy()

    up[up < 0] = 0 # the up dataframe contain only positive values. Those values with a positive difference between close price today and close price yesterday
    down[down > 0] = 0 # the down dataframe contain only positive values. Those values with a negative difference between close price today and close price yesterday
    
    # up means that the prices increase between two consecutive days
    # down means that the prices decrease between two consecutive days
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down=down.ewm(com=period-1, adjust=False).mean().abs()
    # 
    rs = ema_up / ema_down
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi = rsi.dropna()
    return rsi

rsi_values = RSI(df) #rsi_values is a dataframe with the tokens as columns and the rsi values 