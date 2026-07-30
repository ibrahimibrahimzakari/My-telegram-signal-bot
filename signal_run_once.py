#!/usr/bin/env python3
"""
Single-run signal script for GitHub Actions.
- Fetches OHLCV from Binance (public)
- Computes EMA crossover + RSI (Wilder smoothing)
- Sends Telegram message when BUY/SELL condition occurs
Requirements: ccxt, pandas, requests
"""

import os
import sys
import requests
import ccxt
import pandas as pd

# Config (override via env)
SYMBOL = os.getenv("SYMBOL", "BTC/USDT")
TIMEFRAME = os.getenv("TIMEFRAME", "1h")
EMA_FAST = int(os.getenv("EMA_FAST", "9"))
EMA_SLOW = int(os.getenv("EMA_SLOW", "21"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))

# Required secrets (set in GitHub Secrets)
TELEGRAM_TOKEN = os.getenv("#!/usr/bin/env python3
"""
Single-run signal script for GitHub Actions.
- Fetches OHLCV from Binance (public)
- Computes EMA crossover + RSI (Wilder smoothing)
- Sends Telegram message when BUY/SELL condition occurs
Requirements: ccxt, pandas, requests
"""

import os
import sys
import requests
import ccxt
import pandas as pd

# Config (override via env)
SYMBOL = os.getenv("SYMBOL", "BTC/USDT")
TIMEFRAME = os.getenv("TIMEFRAME", "1h")
EMA_FAST = int(os.getenv("EMA_FAST", "9"))
EMA_SLOW = int(os.getenv("EMA_SLOW", "21"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))

# Required secrets (set in GitHub Secrets)
TELEGRAM_TOKEN = os.getenv("8973436194:AAHoHX7Wg6VAV2wl_ulK7iW4psz_wI-0mRo")
TELEGRAM_CHAT_ID = os.getenv("8973436194")


def send_telegram(text):
    """Send a message to Telegram (safe no-op if credentials missing)."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing. Set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID.")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        print("Telegram message sent.")
        return True
    except Exception as e:
        print("Failed to send Telegram message:", e)
        return False


def fetch_ohlcv(symbol, timeframe, limit=200):
    """Fetch OHLCV from Binance using ccxt and return DataFrame indexed by datetime."""
    exchange = ccxt.binance({"enableRateLimit": True})
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=["ts", "open", "high", "low", "close", "volume"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    df.set_index("date", inplace=True)
    return df


def compute_rsi(series, period=14):
    """Compute RSI using Wilder's smoothing (returns a pandas Series)."""
    delta = series.diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)
    # Wilder smoothing uses com=period-1 in ewm
    ma_up = up.ewm(com=period - 1, adjust=False).mean()
    ma_down = down.ewm(com=period - 1, adjust=False).mean()
    rs = ma_up / ma_down
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_indicators(df):
    df["ema_fast"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["rsi"] = compute_rsi(df["close"], RSI_PERIOD)
    return df


def compute_signal(df):
    if len(df) < 3:
        return None, "Not enough data"
    prev = df.iloc[-2]
    last = df.iloc[-1]
    # Bullish crossover
    if prev["ema_fast"] <= prev["ema_slow"] and last["ema_fast"] > last["ema_slow"]:
        if last["rsi"] < RSI_OVERBOUGHT:
            return "BUY", f"EMA{EMA_FAST}>{EMA_SLOW} crossover, RSI={last['rsi']:.1f}"
    # Bearish crossover
    if prev["ema_fast"] >= prev["ema_slow"] and last["ema_fast"] < last["ema_slow"]:
        if last["rsi"] > RSI_OVERSOLD:
            return "SELL", f"EMA{EMA_FAST}<{EMA_SLOW} crossover, RSI={last['rsi']:.1f}"
    return None, "No strong signal"


def main():
    try:
        df = fetch_ohlcv(SYMBOL, TIMEFRAME, limit=200)
    except Exception as e:
        print("Failed to fetch OHLCV:", e)
        sys.exit(1)

    df = compute_indicators(df)
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
    main()")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(text):
    """Send a message to Telegram (safe no-op if credentials missing)."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing. Set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID.")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        print("Telegram message sent.")
        return True
    except Exception as e:
        print("Failed to send Telegram message:", e)
        return False


def fetch_ohlcv(symbol, timeframe, limit=200):
    """Fetch OHLCV from Binance using ccxt and return DataFrame indexed by datetime."""
    exchange = ccxt.binance({"enableRateLimit": True})
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=["ts", "open", "high", "low", "close", "volume"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    df.set_index("date", inplace=True)
    return df


def compute_rsi(series, period=14):
    """Compute RSI using Wilder's smoothing (returns a pandas Series)."""
    delta = series.diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)
    # Wilder smoothing uses com=period-1 in ewm
    ma_up = up.ewm(com=period - 1, adjust=False).mean()
    ma_down = down.ewm(com=period - 1, adjust=False).mean()
    rs = ma_up / ma_down
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_indicators(df):
    df["ema_fast"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["rsi"] = compute_rsi(df["close"], RSI_PERIOD)
    return df


def compute_signal(df):
    if len(df) < 3:
        return None, "Not enough data"
    prev = df.iloc[-2]
    last = df.iloc[-1]
    # Bullish crossover
    if prev["ema_fast"] <= prev["ema_slow"] and last["ema_fast"] > last["ema_slow"]:
        if last["rsi"] < RSI_OVERBOUGHT:
            return "BUY", f"EMA{EMA_FAST}>{EMA_SLOW} crossover, RSI={last['rsi']:.1f}"
    # Bearish crossover
    if prev["ema_fast"] >= prev["ema_slow"] and last["ema_fast"] < last["ema_slow"]:
        if last["rsi"] > RSI_OVERSOLD:
            return "SELL", f"EMA{EMA_FAST}<{EMA_SLOW} crossover, RSI={last['rsi']:.1f}"
    return None, "No strong signal"


def main():
    try:
        df = fetch_ohlcv(SYMBOL, TIMEFRAME, limit=200)
    except Exception as e:
        print("Failed to fetch OHLCV:", e)
        sys.exit(1)

    df = compute_indicators(df)
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
