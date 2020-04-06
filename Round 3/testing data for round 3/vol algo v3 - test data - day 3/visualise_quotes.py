import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as sp


# Time,Competitor,Operation,OrderId,Side,Volume,Price,Lifespan,Fee,FuturePrice,EtfPrice,
# AccountBalance,FuturePosition,EtfPosition,ProfitLoss,TotalFees,MaxDrawdown,BuyVolume,SellVolume

pd.set_option('display.max_rows', None)
df = pd.read_csv("match_events_1.csv")
df.set_index("Time", inplace=True)

traders = df.Competitor.unique()

# Extract instrument prices.
etf_price = df["EtfPrice"]
future_price = df["FuturePrice"]

home = "VolumeAdjustN15_v3"

# trader = "Example2"
trader = "VolumeAdjustN12_v3"
# trader = "L2AverageWtd"

action = "Insert"
# action = "Fill"

default_quote_size = 15   # indentify competitor quotes > this number

# Extract competitior bid quotes.
competitor_bid_df = df.loc[(df['Competitor'] == trader) & (df["Operation"] == action) & (df["Side"] == "B")]
competitor_bid_quotes = competitor_bid_df[["Price", "Volume", "EtfPosition"]]

# Extract ask competitor ask quotes.
competitor_ask_df = df.loc[(df['Competitor'] == trader) & (df["Operation"] == action) & (df["Side"] == "S")]
competitor_ask_quotes = competitor_ask_df[["Price", "Volume", "EtfPosition"]]

# Extract home bid quotes.
home_bid_df = df.loc[(df['Competitor'] == home) & (df["Operation"] == action) & (df["Side"] == "B")]
home_bid_quotes = home_bid_df[["Price", "Volume"]]

# Extract home ask quotes.
home_ask_df = df.loc[(df['Competitor'] == home) & (df["Operation"] == action) & (df["Side"] == "S")]
home_ask_quotes = home_ask_df[["Price", "Volume"]]

# Get total bid/ask volumes.
competitor_bid_volume = df.loc[(df['Competitor'] == trader) & (df["Operation"] == action)]['BuyVolume'].max()
competitor_ask_volume = df.loc[(df['Competitor'] == trader) & (df["Operation"] == action)]['SellVolume'].max()
home_bid_volume = df.loc[(df['Competitor'] == home) & (df["Operation"] == action)]['BuyVolume'].max()
home_ask_volume = df.loc[(df['Competitor'] == home) & (df["Operation"] == action)]['SellVolume'].max()

# Get total number of actions taken.
competitor_bid_count = competitor_bid_quotes.shape[0]
competitor_ask_count = competitor_ask_quotes.shape[0]
home_bid_count = home_bid_quotes.shape[0]
home_ask_count = home_ask_quotes.shape[0]

# Get actions with notable volume.
comp_bids_notable_volume = competitor_bid_quotes.loc[(competitor_bid_quotes['Volume'] > default_quote_size) | (competitor_bid_quotes['Volume'] < -default_quote_size)]
comp_asks_notable_volume = competitor_ask_quotes.loc[(competitor_ask_quotes['Volume'] > default_quote_size) | (competitor_ask_quotes['Volume'] < -default_quote_size)]

print("Total competitor " + action + " bids:", competitor_bid_count)
print("Total competitor " + action + " asks:", competitor_ask_count)
print("Total home " + action + " bids:", home_bid_count)
print("Total home " + action + " ask volume:", home_ask_count, "\n")

print("Total competitor " + action + " bid volume:", competitor_bid_volume)
print("Total competitor " + action + " ask volume:", competitor_ask_volume)
print("Total home " + action + " bid volume:", home_bid_volume)
print("Total home " + action + " ask volume:", home_ask_volume, "\n")

print("Total notable competitior " + action + " bids:", comp_bids_notable_volume.shape[0])
print("Total notable competitior " + action + " asks:", comp_asks_notable_volume.shape[0], "\n")

# Print the notable bids to verify how quote volume interacts with inventory.
# print(comp_bids_notable_volume)
print(competitor_bid_quotes)

plt.plot(etf_price, color='lightblue', linewidth=1, label="ETF Price", alpha=0.4)
plt.plot(future_price, color='purple', lw=1, label="Future Price")
plt.plot(competitor_bid_quotes["Price"], color="darkgreen", lw=1, label="Competitor bids")
plt.plot(competitor_ask_quotes["Price"], color="red", lw=1, label="Competitor asks", alpha=0.5)
plt.plot(home_bid_quotes["Price"], color="lightgreen", lw=1, label="Home bids", alpha=0.4)
plt.plot(home_ask_quotes["Price"], color="magenta", lw=1, label="Home asks", alpha=0.3)

plt.ylabel("Price")
plt.xlabel("Time (seconds")
plt.title(str('Competitor vs home ' + action + 's'), fontsize=14)
plt.legend()
plt.show()