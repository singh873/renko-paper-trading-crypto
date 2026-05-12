import requests
import time
import csv
from datetime import datetime

# ======================
# CONFIG
# ======================
SYMBOL = "BTCUSDT"
BRICK_SIZE = 20
QUANTITY = 1

INITIAL_BALANCE = 1000000000000
balance = INITIAL_BALANCE

position = None
entry_price = None
entry_time = None

renko_bricks = []
last_brick_close = None
last_signal = None

CSV_FILE = "trade_log.csv"

# ======================
# Create CSV File Header
# ======================
with open(CSV_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "Entry Time",
        "Exit Time",
        "Side",
        "Entry Price",
        "Exit Price",
        "Quantity",
        "PnL"
    ])

# ======================
# Fetch Price
# ======================
def fetch_price():
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={SYMBOL}"
    data = requests.get(url).json()
    return float(data["price"])

# ======================
# Renko Logic
# ======================
def build_renko(price):
    global last_brick_close

    if last_brick_close is None:
        last_brick_close = price
        return []

    move = price - last_brick_close
    bricks = []

    while abs(move) >= BRICK_SIZE:
        if move > 0:
            last_brick_close += BRICK_SIZE
            bricks.append("GREEN")
        else:
            last_brick_close -= BRICK_SIZE
            bricks.append("RED")

        move = price - last_brick_close

    return bricks

# ======================
# Calculate Unrealized PnL
# ======================
def calculate_unrealized_pnl(price):
    if position == "LONG":
        return (price - entry_price) * QUANTITY
    elif position == "SHORT":
        return (entry_price - price) * QUANTITY
    else:
        return 0

# ======================
# Log Trade to CSV
# ======================
def log_trade(entry_t, exit_t, side, entry_p, exit_p, pnl):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            entry_t.strftime("%Y-%m-%d %H:%M:%S"),
            exit_t.strftime("%Y-%m-%d %H:%M:%S"),
            side,
            round(entry_p, 2),
            round(exit_p, 2),
            QUANTITY,
            round(pnl, 4)
        ])
    print(f"✅ Trade Logged | Realized PnL: {round(pnl,4)}")

# ======================
# Execute Trade
# ======================
def execute_trade(signal, price):
    global position, entry_price, entry_time, balance

    current_time = datetime.now()

    # Close opposite position first
    if position == "LONG" and signal == "SELL":
        pnl = (price - entry_price) * QUANTITY
        log_trade(entry_time, current_time, "LONG", entry_price, price, pnl)
        balance += pnl
        position = None

    elif position == "SHORT" and signal == "BUY":
        pnl = (entry_price - price) * QUANTITY
        log_trade(entry_time, current_time, "SHORT", entry_price, price, pnl)
        balance += pnl
        position = None

    # Open new position
    if signal == "BUY":
        position = "LONG"
        entry_price = price
        entry_time = current_time
        print(f"📈 LONG OPENED at {price}")

    elif signal == "SELL":
        position = "SHORT"
        entry_price = price
        entry_time = current_time
        print(f"📉 SHORT OPENED at {price}")

# ======================
# Signal Logic
# ======================
def check_signal():
    global last_signal

    if len(renko_bricks) < 2:
        return None

    last_two = renko_bricks[-2:]

    if last_two == ["GREEN", "GREEN"] and last_signal != "BUY":
        last_signal = "BUY"
        return "BUY"

    if last_two == ["RED", "RED"] and last_signal != "SELL":
        last_signal = "SELL"
        return "SELL"

    return None

# ======================
# MAIN LOOP
# ======================
print("🚀 PAPER TRADING BOT WITH CSV LOG STARTED\n")

while True:
    try:
        price = fetch_price()
        new_bricks = build_renko(price)

        for brick in new_bricks:
            renko_bricks.append(brick)
            signal = check_signal()

            if signal:
                execute_trade(signal, price)

        unrealized_pnl = calculate_unrealized_pnl(price)

        print(
            f"Price: {price} | "
            f"Position: {position} | "
            f"Balance: {round(balance,2)} | "
            f"Live PnL: {round(unrealized_pnl,4)}"
        )
        time.sleep(2)

    except Exception as e:
        print("Error:", e)
        time.sleep(5)