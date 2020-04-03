import pandas as pd
import numpy as np


# Time,Competitor,Operation,OrderId,Side,Volume,Price,Lifespan,Fee,FuturePrice,EtfPrice,
# AccountBalance,FuturePosition,EtfPosition,ProfitLoss,TotalFees,MaxDrawdown,BuyVolume,SellVolume

df = pd.read_csv("match31_events.csv")

teams = df.Competitor.unique()
stats = {}

for i in teams:
    pnl = df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['ProfitLoss'].max()
    fees = df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['TotalFees'].max()
    buy_vol = df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['BuyVolume'].max()
    sell_vol = df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['SellVolume'].max()
    stats[i] = {
                    "pnl": pnl,
                    "fees": fees,
                    "buy_vol": buy_vol,
                    "sell_vol": sell_vol
                }


for i in teams:
    print("Strategy", i, "---")
    print("PnL:", stats[i]["pnl"])
    print("Fees:", stats[i]["fees"])
    print("Buy vol:", stats[i]["buy_vol"])
    print("Sell vol:", stats[i]["sell_vol"], "\n")
