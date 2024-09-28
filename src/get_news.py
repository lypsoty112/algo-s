from typing import Dict, List
from loguru import logger
from newsapi import NewsApiClient

from src.config import Settings

settings = Settings()
newsapi = NewsApiClient(api_key=settings.NEWS_API_API_KEY)

def get_news() -> List[Dict]:
    headlines = newsapi.get_top_headlines(country="us", category="business")
    assert headlines.get("status", "not ok") == "ok", f'status: {headlines.get("status", "not ok")}'
    logger.info(f"Got {headlines.get('totalResults')} results.")
    
    # Return the articles
    return headlines.get('articles', [])


def get_news_ticker(ticker: str) -> List[Dict]:
    articles = newsapi.get_everything(q=f'"{ticker}"')
    logger.info(f"Got {articles.get('totalResults')} results for ticker {ticker}")
    articles = articles.get('articles', [])
    return articles[:100]