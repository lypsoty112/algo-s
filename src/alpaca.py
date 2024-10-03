
from typing import List, Dict
from src.config import Settings
import requests


settings = Settings()
HEADERS = {
    "accept": "application/json",
    "APCA-API-KEY-ID": settings.ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": settings.ALPACA_SECRET_KEY
}

def get_open_postions() -> List[Dict]:
    url = "https://paper-api.alpaca.markets/v2/positions"

    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_cash() -> float:
    url = "https://paper-api.alpaca.markets/v2/account"

    response = requests.get(url, headers=HEADERS)
    response = response.json()
    return float(response.get('cash', 0))

def check_if_tradeable(ticker: str) -> bool:
    url = f"https://paper-api.alpaca.markets/v2/assets/{ticker}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        response = response.json()
        return response.get('status', 'inactive') == 'active' and response.get('tradable', False)
    return False

def buy_ticker(ticker: str):
    portfolio = get_open_postions()
    symbols = [x.get('symbol', None) for x in portfolio]
    if ticker in symbols:
        return
    
    url = "https://paper-api.alpaca.markets/v2/orders"
    cash = get_cash()

    # Divide the cash by the number of open positions
    assert settings.MAX_STOCKS != len(portfolio)
    notional = round(cash / (settings.MAX_STOCKS - len(portfolio)), 2)

    body = {
        "symbol": ticker,
        "side": 'buy',
        "notional": notional,
        "type": "market",
        "time_in_force": 'day'

    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        **HEADERS
    }

    response = requests.post(url, headers=headers, json=body)
    assert response.status_code == 200, f'Expected 200, got {response.status_code}: {response.json()}'
    return


def sell_ticker(ticker: str):
    portfolio = get_open_postions()
    symbols = [x.get('symbol', None) for x in portfolio]
    if ticker not in symbols:
        return
    
    url = "https://paper-api.alpaca.markets/v2/orders"
    body = {
        "symbol": ticker,
        "side": 'sell',
        "type": "market",
        "time_in_force": 'day'

    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        **HEADERS
    }

    response = requests.post(url, headers=headers, json=body)
    assert response.status_code == 200, f'Expected 200, got {response.status_code}: {response.json()}'
    return

