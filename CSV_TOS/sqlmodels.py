from sqlalchemy import create_engine
from functions import Backtest
import pandas as pd
import numpy as np

class StoreData():
    engine = create_engine('sqlite:///new.db', echo = False)
    df.to_sql('results', con=engine,if_exists='append')


def summary(df):
    return df[['ticker','total_profit','total_trades','win_ratio','loss_ratio','expectency','win_avg','loss_avg','reward_risk_ratio']]

def storeit(file):
    conn = engine.connect()
    data=Backtest(file).result()
    conn.execute(result.insert(),data)
    print('Done!')
    df=pd.read_sql_table('result',con=engine).sort_values(by='id',ascending=False).set_index('id') 
    return summary(df[df['ticker']==Backtest(file).ticker]).transpose()
    
    
def showit(info=2):
    conn = engine.connect()
    df=pd.read_sql_table('result',con=engine).sort_values(by='id',ascending=False).set_index('id') 
    if info==0:
        return df
    elif info==1:
        return df.transpose()
    else:
        return summary(df).transpose()

def companylist(sql='SELECT DISTINCT ticker from result;'):
    conn = engine.connect()
    command = text(sql)
    result = conn.execute(sql)
    conn.close()
    return result

def check_ticker(tickers,info=2):
    conn = engine.connect()
    df=pd.read_sql_table('result',con=engine).sort_values(by='id',ascending=False).set_index('id') 
    conn.close()
    if info==0:
        return df[df['ticker']==tickers]
    elif info==1:
        return df[df['ticker']==tickers].transpose()
    else:
        return summary(df[df['ticker']==tickers]).transpose()
