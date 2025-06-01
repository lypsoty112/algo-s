from datetime import datetime, timedelta
from loguru import logger
from src.config import Settings
from typing import Literal

api_key = Settings().POLYGON_API_KEY


def get_market_trends(time_frame: Literal["day", "week", "month", "6 months"]) -> dict:
    # TODO: Get market trends
    MARKETS = ["S&P", "DOW", "Nasdaq", "FTSE 100", "DAX"]


def get_financial_data(ticker: str) -> dict:
    # TODO: Get financial data from polygon
    pass
