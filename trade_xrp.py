import logging
import time
from datetime import datetime
from alpaca_trade_api.rest import REST, APIError
from config import API_KEY, SECRET_KEY, BASE_URL

# --- Configuration ---
SYMBOL = "XRP/USD"        # Must use slash format for crypto
NOTIONAL = 10              # Dollar amount to buy
RETRY_DELAY = 10           # Seconds between checks
PRICE_DIFF_THRESHOLD = 0.01  # Minimum price movement to act on

# --- Logging ---
logging.basicConfig(
    filename="xrp_trade.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- Initialize Alpaca API ---
api = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")

last_price = None

def print_account_info():
    try:
        account = api.get_account()
        balance = account.cash
        print(f"[{datetime.now()}] Account balance: ${balance}")
        logging.info(f"Account balance: ${balance}")
    except APIError as e:
        logging.error(f"Failed to fetch account info: {e}")
        print(f"[{datetime.now()}] Failed to fetch account info: {e}")

def print_positions():
    try:
        positions = api.list_positions()
        if not positions:
            print(f"[{datetime.now()}] No current holdings.")
            logging.info("No current holdings.")
        else:
            print(f"[{datetime.now()}] Current holdings:")
            logging.info("Current holdings:")
            for p in positions:
                message = f"{p.symbol}: {p.qty} @ ${p.avg_entry_price}"
                print(f"  {message}")
                logging.info(message)
    except APIError as e:
        logging.error(f"Failed to fetch positions: {e}")
        print(f"[{datetime.now()}] Failed to fetch positions: {e}")

def get_current_price():
    try:
        trade = api.get_crypto_latest_trade("XRP/USD")
        return float(trade.price)
    except Exception as e:
        logging.error(f"Failed to fetch trade: {e}")
        print(f"[{datetime.now()}] Failed to fetch trade: {e}")
        return None

def buy():
    try:
        api.submit_order(
            symbol=SYMBOL,
            notional=str(NOTIONAL),
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        print(f"[{datetime.now()}] Buy order submitted for ${NOTIONAL} of {SYMBOL}")
        logging.info(f"Buy order submitted for ${NOTIONAL} of {SYMBOL}")
    except APIError as e:
        print(f"[{datetime.now()}] Buy failed: {e}")
        logging.error(f"Buy failed: {e}")

def sell():
    try:
        position = api.get_position(SYMBOL.replace("/", ""))
        api.submit_order(
            symbol=SYMBOL,
            qty=position.qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
        print(f"[{datetime.now()}] Sell order submitted for all {SYMBOL} holdings")
        logging.info(f"Sell order submitted for all {SYMBOL} holdings")
    except APIError as e:
        print(f"[{datetime.now()}] Sell failed: {e}")
        logging.error(f"Sell failed: {e}")

def main():
    global last_price
    print(f"[{datetime.now()}] Starting real-time XRP strategy")
    logging.info("Starting real-time XRP strategy")

    try:
        while True:
            print_account_info()
            print_positions()

            price = get_current_price()
            if price is None:
                time.sleep(RETRY_DELAY)
                continue

            print(f"[{datetime.now()}] Current XRP/USD price: ${price}")

            if last_price is None:
                last_price = price
                print(f"[{datetime.now()}] Initial price set. Waiting for next cycle.")
                time.sleep(RETRY_DELAY)
                continue

            price_change = price - last_price

            if price_change >= PRICE_DIFF_THRESHOLD:
                print(f"[{datetime.now()}] Price increased by {price_change:.5f}. Selling.")
                sell()
            elif price_change <= -PRICE_DIFF_THRESHOLD:
                print(f"[{datetime.now()}] Price decreased by {abs(price_change):.5f}. Buying.")
                buy()
            else:
                print(f"[{datetime.now()}] Price change {price_change:.5f} is too small. No action.")

            last_price = price
            time.sleep(RETRY_DELAY)
    except KeyboardInterrupt:
        print(f"[{datetime.now()}] Script interrupted. Exiting...")
        logging.info("Script interrupted and exiting.")

if __name__ == "__main__":
    main()