import pandas as pd
import matplotlib.pyplot as plt

def demanddata():
    df = pd.read_csv('helen_2015_2021b.csv',sep = ';', decimal=',')

    df.columns = ['Date', 'Consumption']
    df = df.loc[26306:35065]
    df['Date']= pd.to_datetime(df['Date'], format='%d.%m.%Y %H:%M')
    df['Date'] = pd.to_datetime(df["Date"].dt.strftime('%Y-%m-%d %H'))
    df["Consumption"] = pd.to_numeric(df["Consumption"])
    print(df.head())
    
    return df

