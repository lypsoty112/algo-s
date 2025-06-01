from alpaca.trading.client import TradingClient
from src.core.config import settings

client = TradingClient(
    api_key=settings.ALPACA_API_KEY,
    api_secret=settings.ALPACA_SECRET_KEY,
    paper=settings.PAPER_TRADING,
)
