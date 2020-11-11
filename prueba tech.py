#import ffn
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#import pandas_datareader.data as web
import datetime as dt
#import fix_yahoo_finance as yf

#from pandas_datareader import data, wb
import requests
import urllib.parse
import scipy.optimize as optimize
from scipy.optimize import fsolve
#import eikon as ek
import configparser as cp
from pandas.tseries.offsets import BDay
import streamlit as st
import yfinance as yf


def tech_momentum_new(ticker, start = "2000-01-01",interval = "1d", mom = 20,buy_zone = 0.5,sell_zone = 1.04):
    df = yf.download(ticker, start = start, interval = interval)
    df["mom"] = df["Close"].pct_change(mom)
    df["mom avg"] = df["mom"].mean()
    df["buyzone"] = df["mom avg"] - df["mom avg"] * buy_zone
    df["+std"] = df["mom avg"] + df["mom"].std()
    df["sell"] = df["mom avg"] * sell_zone
    df = df.reset_index().dropna()
    df = df.reset_index()
    index = df["index"].loc[0]
    df = df.dropna()
    
    #Sistema
    
    trades = []
    k = 0
    
    for f in range(index,len(df)):
        if(f + k <= len(df)):
            if(df.loc[f + k,"mom"] <= df.loc[f + k,"buyzone"]):
                trade_idx = f + k
                trade = {}
                for k in range(f + k,len(df)):
                    if(df.loc[k,"mom"] >= df.loc[k,"sell"]):
                        trade["Date in"] = df.loc[trade_idx,"Date"]
                        trade["Date out"] = df.loc[k,"Date"]
                        trade["Diff dates"] = trade["Date out"] - trade["Date in"]
                        trade["momentum in"] = df.loc[trade_idx,"mom"]
                        trade["momentum buyzone"] = df.loc[trade_idx,"buyzone"]
                        trade["Price in"] = df.loc[trade_idx,"Close"]
                        trade["Price out"] = df.loc[k,"Close"]
                        trade["rend"] = (trade["Price out"] / trade["Price in"] - 1) * 100
                        trades.append(trade)
                        break
                        
    tradesTabla2 = pd.DataFrame(trades)
    tradesTabla2["rend_comp"] = ((tradesTabla2["rend"]/100+1).cumprod() -1)*100
    #Calculos finales
    positivos = tradesTabla2["rend"].loc[tradesTabla2["rend"] > 0].count()
    negativos = tradesTabla2["rend"].loc[tradesTabla2["rend"] < 0].count()
    porcentaje_w = round(positivos / (positivos+negativos) * 100,2)
    
    avg_ret = tradesTabla2["rend"].mean()
    min_ret = tradesTabla2["rend"].min()
    max_ret = tradesTabla2["rend"].max()
    #print(rsi)
    
    
    
    #print("Cantidad de trades positivos:", positivos)
    #print("cantidad de trades negativos:", negativos)
    #print("Total trades", positivos + negativos)
    #print("El porcentaje de ganadores es", porcentaje_w,"%")
    #print("El porcentaje de perdedores es", 100 - porcentaje_w,"%")
    #print("el retorno promedio de la estrategia para ", ticker, "es:",np.round(avg_ret,2))
    #print("el retorno minimo de la estrategia es:",np.round(min_ret,2))
    #print("el retorno maximo de la estrategia es:", np.round(max_ret,2))
    #return tradesTabla2.round(2)
    pack = {"retorno promedio":  np.round(avg_ret,2),
            "% ganadores": np.round(porcentaje_w,2),
            "% perdedores": 100 - porcentaje_w,
            "retorno minimo": np.round(min_ret,2),
            "retorno maximo": np.round(max_ret,2),
        
    }
    return pack
st.title("Estrategia Momentum")

accion = st.text_input("ticker:")
momentum = st.slider('Momentum', 0,100)
buy = st.slider('buy zone', 0.01,0.99)





estrategia = tech_momentum_new(accion, mom = momentum, buy_zone = buy)
st.write(estrategia)

