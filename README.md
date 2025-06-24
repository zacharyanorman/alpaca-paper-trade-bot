# XRP Trade Bot

This bot uses the Alpaca API to paper trade XRP/USD based on price movement thresholds.

## Features

- Buys or sells based on price increases or drops of $0.01 or more.
- Logs all activity to `xrp_trade.log`.
- Uses the Alpaca paper trading API.

## Setup

1. Install dependencies:
    pip install alpaca-trade-api

2. Set your Alpaca credentials in `config.py`.

3. Run the script:
    python trade_xrp.py
