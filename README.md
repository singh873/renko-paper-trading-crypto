# Renko Paper Trading Crypto

A Python-based cryptocurrency paper trading system using the Renko chart strategy with live Binance market data.

## Features

- Live BTCUSDT price tracking
- Renko brick generation
- Automated BUY/SELL signals
- Paper trading simulation
- Real-time PnL tracking
- CSV trade logging

## Tech Stack

- Python
- Binance API
- Requests
- CSV

## Strategy Logic

- 2 consecutive GREEN bricks → BUY
- 2 consecutive RED bricks → SELL

The system automatically closes opposite positions before opening a new trade.

## Installation

```bash
git clone https://github.com/singh873/renko-paper-trading-crypto.git
cd renko-paper-trading-crypto
pip install -r requirements.txt
