import pandas as pd
import numpy as np

# Time,Competitor,Operation,OrderId,Side,Volume,Price,Lifespan,Fee,FuturePrice,EtfPrice,
# AccountBalance,FuturePosition,EtfPosition,ProfitLoss,TotalFees,MaxDrawdown,BuyVolume,SellVolume

total_matches = 6

matches = [pd.read_csv("match_events_" + str(i) + ".csv", low_memory=False) for i in range(1, total_matches + 1)]

traders = matches[0].Competitor.unique()

tally = {i: {"pnl": 0, "fees": 0, "buy_vol": 0, "sell_vol": 0} for i in traders}

# Sum all the values.
for df in matches:
    for i in traders:
        tally[i]['pnl'] += df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['ProfitLoss'].max()
        tally[i]['fees'] += df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['TotalFees'].max()
        tally[i]['buy_vol'] += df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['BuyVolume'].max()
        tally[i]['sell_vol'] += df.loc[(df['Competitor'] == i) & (df["Operation"] == 'Fill')]['SellVolume'].max()

# Print averaged result.
for i in traders:
    print("Strategy", i, "---")
    print("avg PnL:", tally[i]['pnl'] / total_matches)
    print("avg Fees:", tally[i]['fees'] / total_matches)
    print("avg Buy vol:", tally[i]['buy_vol'] / total_matches)
    print("avg Sell vol:", tally[i]['sell_vol'] / total_matches, "\n")
