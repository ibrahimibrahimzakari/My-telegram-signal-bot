#!/usr/bin/env python3
"""
Minimal single-run signal generator for GitHub Actions (stateless).
- Fetches OHLCV from Binance (public)
- Computes EMA crossover + RSI filter
- Sends a Telegram message if a BUY or SELL signal occurs
"""

import os
import sys
import requests
import ccxt
import pandas as pd
import pandas_ta as ta

# Config (override via env)
SYMBOL = os.getenv("SYMBOL", "BTC/USDT")
TIMEFRAME = os.getenv("TIMEFRAME", "1h")
EMA_FAST = int(os.getenv("EMA_FAST", "9"))
EMA_SLOW = int(os.getenv("EMA_SLOW", "21"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))

# Required env secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing. Set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("Telegram message sent.")
    except Exception as e:
        print("Failed to send Telegram message:", e)

def fetch_ohlcv(symbol, timeframe, limit=200):
    exchange = ccxt.binance({"enableRateLimit": True})
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=["ts","open","high","low","close","volume"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    df.set_index("date", inplace=True)
    return df

def compute_signal(df):
    df["ema_fast"] = ta.ema(df["close"], length=EMA_FAST)
    df["ema_slow"] = ta.ema(df["close"], length=EMA_SLOW)
    df["rsi"] = ta.rsi(df["close"], length=RSI_PERIOD)

    if len(df) < 3:
        return None, "Not enough data"

    prev = df.iloc[-2]
    last = df.iloc[-1]

    # Bullish crossover
    if prev["ema_fast"] <= prev["ema_slow"] and last["ema_fast"] > last["ema_slow"]:
        if last["rsi"] < RSI_OVERBOUGHT:
            return "BUY", f"EMA{EMA_FAST}>{EMA_SLOW} crossover and RSI={last['rsi']:.1f}"
    # Bearish crossover
    if prev["ema_fast"] >= prev["ema_slow"] and last["ema_fast"] < last["ema_slow"]:
        if last["rsi"] > RSI_OVERSOLD:
            return "SELL", f"EMA{EMA_FAST}<{EMA_SLOW} crossover and RSI={last['rsi']:.1f}"

    return None, "No strong signal"

def main():
    try:
        df = fetch_ohlcv(SYMBOL, TIMEFRAME, limit=200)
    except Exception as e:
        print("Failed to fetch OHLCV:", e)
        sys.exit(1)

    signal, reason = compute_signal(df)
    last_price = df["close"].iloc[-1]
    ts = df.index[-1].isoformat()

    if signal:
        text = (
            f"*Signal*: {signal}\n"
            f"*Pair*: {SYMBOL}\n"
            f"*TF*: {TIMEFRAME}\n"
            f"*Price*: {last_price:.2f}\n"
            f"*Reason*: {reason}\n"
            f"_Time_: {ts}"
        )
        send_telegram(text)
        print("Signal sent:", signal)
    else:
        print("No signal:", reason)

if __name__ == "__main__":
    main()