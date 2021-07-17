import pandas as pd
import numpy as np
import json
import datetime
from datetime import date
from sqlalchemy import create_engine
engine = create_engine('sqlite:///new.db', echo = False)

def clean_data(file):
        #read file
        df = pd.read_csv("./CSV/"+file+".csv",sep=';',skiprows=3)
        #remove unwanted rows
        df = df.iloc[:,:-1]
        #read time  and date then make time as index
        df['start']=pd.to_datetime(df['Date/Time'],format='%m/%d/%y, %I:%M %p')
        df=df.set_index(['Id']).rename(columns={'Price':'open_trade'})
        #drop Id and unnamed column
        df.drop(["P/L","Trade P/L","Side","Date/Time"],axis=1,inplace=True)
        # drop last n rows
        df.drop(df.tail(3).index,inplace=True)
        try:
            information=df['Strategy'].iloc[1].split(',')
            information[5]
        except:
            information=df['Strategy'].iloc[0].split(',')
            information[5]
        #add open trade and remove unwanted symbols
        df['open_trade'] = df['open_trade'].map(lambda x: x.lstrip('($').rstrip(')')).str.replace(',','')
        #add close time of trade to same row of start time by shifting start row
        df['end']=df["start"].shift(-1, axis = 0)
        #add duration column
        df['duration']=df.end-df.start
        #add close price of trade to same row of start price by shifting start row
        df['close_trade']=df["open_trade"].shift(-1, axis = 0)
        #convert to numers
        df['open_trade']=pd.to_numeric(df['open_trade'])
        df['close_trade']=pd.to_numeric(df['close_trade'])
        #add profit column
        df['profit']=(df.close_trade-df.open_trade)*df.Amount
        df['percent']=df.profit*100/(df.open_trade*df.Amount)
        df=df[::2].dropna()
        #add win column
        df['win'] = np.where(df['profit']>0, True, False)
        #add sum_profit profit column
        # set index
        df.set_index(['start'],inplace = True)
        #retrurn dataframe
        return df,information
class Backtest:
    def __init__(self,file):
        self.report_date=date.today().strftime("%m/%d/%y")
        self.file=file
        self.df=clean_data(file=self.file)[0]
        self.strategy=clean_data(self.file)[1][0].strip('(')
        self.ticker=clean_data(self.file)[1][2]
        self.timeframe=int(clean_data(self.file)[1][1])
        self.range=180#(self.df.index[-1]-self.df.index[0]).days
        self.position_size=int(self.df['Amount'].iloc[0])
        self.sma=int(clean_data(self.file)[1][3])
        self.ema=int(clean_data(self.file)[1][4])
        self.worktime=int(clean_data(self.file)[1][5])
        self.smooth=int(clean_data(self.file)[1][6])
        self.total_profit=self.df['profit'].sum()
        self.total_trades=len(self.df[self.df['open_trade'] > 0])
        self.win_trades = len(self.df[self.df['profit'] > 0])
        self.loss_trades=len(self.df[self.df['profit'] < 0])
        self.breakeven=len(self.df[self.df['profit'] == 0])
        self.win_avg=self.df.groupby(['win']).mean().at[True,'profit']
        self.loss_avg=self.df.groupby(['win']).mean().at[False,'profit']
        self.reward_risk_ratio=abs(self.win_avg/self.loss_avg)
        self.win_ratio=self.win_trades/self.total_trades
        self.loss_ratio=self.loss_trades/self.total_trades
        self.expectency=self.total_profit/self.total_trades
        self.max_down=self.df['profit'].cumsum().min()
        self.max_up=self.df['profit'].cumsum().max()
        
    def __repr__(self):
        return __name__
    def result(self):
        dic={}
        dic['report_date']=[self.report_date]
        dic['file']=[self.file]
        dic['strategy']=[self.strategy]
        dic['ticker']=[self.ticker]
        dic['timeframe']=[self.timeframe]
        dic['range']=[self.range]
        dic['position_size']=[self.position_size]
        dic['sma']=[self.sma]
        dic['ema']=[self.ema]
        dic['worktime']=[self.worktime]
        dic['smooth']=[self.smooth]
        dic['total_profit']=[self.total_profit]
        dic['total_trades']=[self.total_trades]
        dic['win_trades']=[self.win_trades]
        dic['loss_trades']=[self.loss_trades]
        dic['breakeven']=[self.breakeven]
        dic['win_avg']=[self.win_avg]
        dic['loss_avg']=[self.loss_avg]
        dic['reward_risk_ratio']=[self.reward_risk_ratio]
        dic['win_ratio']=[self.win_ratio]
        dic['loss_ratio']=[self.loss_ratio]
        dic['expectency']=[self.expectency]
        dic['max_down']=[self.max_down]
        dic['max_up']=[self.max_up]
        return dic
    def json_result(self):
        return json.dumps(self.result())
    def print_unit(self,s,num,unit=''):
        print(s,'=',round(num, 2),unit)
    
    def report(self):
        print("#Work: ",self.worktime,"min")
        self.print_unit("#Total profit",self.total_profit,"$")
        self.print_unit("#Total trades",self.total_trades,"trades")
        print("#Expectency",round(self.total_profit/self.total_trades,4),"$")
        self.print_unit("#Win Ratio",self.win_ratio*100,"%")
        self.print_unit("#Loss Ratio",self.loss_ratio*100,"%")
        self.print_unit("#Win average ",self.win_avg,"$")
        self.print_unit("#Loss average ",self.loss_avg,"$")
        self.print_unit("#Reward/Risk ratio",abs(self.reward_risk_ratio),"")
      
    def summary(self,df):
        return df[['ticker','total_profit','total_trades','win_ratio','loss_ratio','expectency','win_avg','loss_avg','reward_risk_ratio']]
 
    def save_report(self):
        df =pd.DataFrame(Backtest(self.file).result())
        engine = create_engine('sqlite:///new.db', echo = False)
        df.to_sql('results', con=engine,if_exists='append',index=False)
        print('Done!')
        display(self.look_up(self.ticker))
        
    def show_db(self,info=2):
        conn = engine.connect()
        df=pd.read_sql_table('results',con=engine).sort_values(by='id',ascending=False).set_index('id') 
        if info==0:
            return df
        elif info==1:
            return df.transpose()
        else:
            return self.summary(df).transpose()
    
    def look_up(self,ticker,info=2):
        conn = engine.connect()
        df=pd.read_sql_table('results',con=engine).sort_values(by='id',ascending=False).set_index('id') 
        conn.close()
        if info==0:
            return df[df['ticker']==ticker]
        elif info==1:
            return df[df['ticker']==ticker].transpose()
        else:
            return self.summary(df[df['ticker']==ticker]).transpose()
