import numpy as np

s_price = 150       # instrument price
sigma = 2           # variance of instrument price
inv = 5             # inventory (total number of lots/shares)
gamma = 0.01        # risk factor
k = 1.5             # rate of arrival of new agressor orders

print("Instrument price:", s_price)
print("Inventory:", inv)
print("Risk factor:", gamma)
print("Price variance:", sigma)
print("Rate of arrival of aggressor orders:", k, "p/sec")

# Naive (symmetric) quote strategy based on price volatility.
spread = gamma * sigma**2 + (2/gamma) * np.log(1 + (gamma / k))
print("\nNaive (symmetric) strategy:", "\n************")
print("Naive spread:", spread)
print("Naive bid:", s_price - spread / 2)
print("Naive ask:", s_price + spread / 2)

# Inventory-aware quote strategy. Skews quotes to offload inventory.
res_price = s_price - inv * gamma * sigma**2
spread = (gamma * sigma**2 + (2 / gamma) * np.log(1 + (gamma / k))) / 2
if res_price >= s_price:
    bid = spread - (res_price - s_price)
    ask = spread + (res_price - s_price)
else:
    bid = spread + (s_price - res_price)
    ask = spread - (s_price - res_price)
print("\nInventory-aware strategy:", "\n************")
print("Reservation price:", res_price)
print("Inventory-aware spread:", bid + ask)
print("Inventory-aware bid spread:", bid)
print("Inventory-aware ask spread:", ask)
print("Inventory-aware bid:", s_price - bid)
print("Inventory-aware ask:", s_price + ask)
