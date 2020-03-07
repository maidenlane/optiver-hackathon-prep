ob = {
    "ask_prices": [11700, 11800, 11900, 12000, 12100],
    "ask_volumes": [1250, 920, 600, 250, 1410],
    "bid_prices": [11600, 11400, 11300, 11200, 10900],
    "bid_volumes": [1650, 400, 1120, 990, 1110]
    }


# 1. Spread /2, naive theoretical price.
bid = ob['bid_prices'][0]
ask = ob['ask_prices'][0]
print("Naive (no liquidity factor) midpoint price:", (ask + bid) / 2)
print("Best bid:", bid)
print("Best ask:", ask)

# 2. Average of book levels 1-3.
bid = (
        (ob['bid_prices'][0] * ob['bid_volumes'][0] +
            ob['bid_prices'][1] * ob['bid_volumes'][1] +
            ob['bid_prices'][2] * ob['bid_volumes'][2]) /
        (ob['bid_volumes'][0] + ob['bid_volumes'][1] +
            ob['bid_volumes'][2]))
ask = (
        (ob['ask_prices'][0] * ob['ask_volumes'][0] +
            ob['ask_prices'][1] * ob['ask_volumes'][1] +
            ob['ask_prices'][2] * ob['ask_volumes'][2]) /
        (ob['ask_volumes'][0] + ob['ask_volumes'][1] +
            ob['ask_volumes'][2]))

print("\nL1-3 mean midpoint price:", (ask + bid) / 2)
print("Mean bid:", bid)
print("Mean ask:", ask)

# 3. Weighted average of book levels L1-3 L1:50% L2:35% L3:15%
w_l1 = 0.5
w_l2 = 0.35
w_l3 = 0.15
bid = (
        (((ob['bid_prices'][0] * ob['bid_volumes'][0]) * w_l1) +
            ((ob['bid_prices'][1] * ob['bid_volumes'][1]) * w_l2) +
            ((ob['bid_prices'][2] * ob['bid_volumes'][2]) * w_l3)) /
        (ob['bid_volumes'][0] * w_l1 + ob['bid_volumes'][1] * w_l2 +
            ob['bid_volumes'][2] * w_l3))
ask = (
        (((ob['ask_prices'][0] * ob['ask_volumes'][0]) * w_l1) +
            ((ob['ask_prices'][1] * ob['ask_volumes'][1]) * w_l2) +
            ((ob['ask_prices'][2] * ob['ask_volumes'][2]) * w_l3)) /
        (ob['ask_volumes'][0] * w_l1 + ob['ask_volumes'][1] * w_l2 +
            ob['ask_volumes'][2] * w_l3))

print("\nL1-3 weighted average 60/30/10 price:", (ask + bid) / 2)
print("Weighted average bid:", bid)
print("Weighted average ask:", ask)

# 4. Average of book levels 1-5.
bid = (
        (ob['bid_prices'][0] * ob['bid_volumes'][0] +
            ob['bid_prices'][1] * ob['bid_volumes'][1] +
            ob['bid_prices'][2] * ob['bid_volumes'][2] +
            ob['bid_prices'][3] * ob['bid_volumes'][3] +
            ob['bid_prices'][4] * ob['bid_volumes'][4]) /
        (ob['bid_volumes'][0] + ob['bid_volumes'][1] +
            ob['bid_volumes'][2] + ob['bid_volumes'][3] +
            ob['bid_volumes'][4]))
ask = (
        (ob['ask_prices'][0] * ob['ask_volumes'][0] +
            ob['ask_prices'][1] * ob['ask_volumes'][1] +
            ob['ask_prices'][2] * ob['ask_volumes'][2] +
            ob['ask_prices'][3] * ob['ask_volumes'][3] +
            ob['ask_prices'][4] * ob['ask_volumes'][4]) /
        (ob['ask_volumes'][0] + ob['ask_volumes'][1] +
            ob['ask_volumes'][2] + ob['ask_volumes'][3] +
            ob['ask_volumes'][4]))

print("\nL1-5 mean midpoint price:", (ask + bid) / 2)
print("Mean bid:", bid)
print("Mean ask:", ask)

# 5. Weighted average of book levels L1-5 L1:37.5% L2:27.5% L3:15% L4:10% L5:5%
w_l1 = 0.375
w_l2 = 0.275
w_l3 = 0.15
w_l4 = 0.10
w_l5 = 0.05
bid = (
        (ob['bid_prices'][0] * ob['bid_volumes'][0] * w_l1 +
            ob['bid_prices'][1] * ob['bid_volumes'][1] * w_l2 +
            ob['bid_prices'][2] * ob['bid_volumes'][2] * w_l3 +
            ob['bid_prices'][3] * ob['bid_volumes'][3] * w_l4 +
            ob['bid_prices'][4] * ob['bid_volumes'][4] * w_l5) /
        (ob['bid_volumes'][0] * w_l1 + ob['bid_volumes'][1] * w_l2 +
            ob['bid_volumes'][2] * w_l3 + ob['bid_volumes'][3] * w_l4 +
            ob['bid_volumes'][4] * w_l5))
ask = (
        (ob['ask_prices'][0] * ob['ask_volumes'][0] * w_l1 +
            ob['ask_prices'][1] * ob['ask_volumes'][1] * w_l2 +
            ob['ask_prices'][2] * ob['ask_volumes'][2] * w_l3 +
            ob['ask_prices'][3] * ob['ask_volumes'][3] * w_l4 +
            ob['ask_prices'][4] * ob['ask_volumes'][4] * w_l5) /
        (ob['ask_volumes'][0] * w_l1 + ob['ask_volumes'][1] * w_l2 +
            ob['ask_volumes'][2] * w_l3 + ob['ask_volumes'][3] * w_l4 +
            ob['ask_volumes'][4] * w_l5))

print("\nL1-5 weighted average 37.5/27.5/15/10/5 price:", (ask + bid) / 2)
print("Weighted average bid:", bid)
print("Weighted average ask:", ask)