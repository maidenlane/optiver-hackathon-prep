import pandas as pd
import numpy as np


# Time,Competitor,Operation,OrderId,Side,Volume,Price,Lifespan,Fee,FuturePrice,EtfPrice,
# AccountBalance,FuturePosition,EtfPosition,ProfitLoss,TotalFees,MaxDrawdown,BuyVolume,SellVolume

df = pd.read_csv("match30_events.csv")

traders = df.Competitor.unique()

for i in traders:
    print("Strategy", i, "---")
    print("PnL:", df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['ProfitLoss'].sum())
    print("Fees:", df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['Fee'].sum())
    print("Buy vol:", df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['BuyVolume'].max())
    print("Sell vol:", df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['SellVolume'].max(), "\n")
