import requests
import time
from datetime import datetime, timedelta
from loguru import logger
from src.config import Settings

api_key = Settings().POLYGON_API_KEY


def get_financial_data(ticker: str) -> dict:
    base_url = "https://api.polygon.io"
    
    def make_request(endpoint: str, params: dict) -> dict:
        url = f"{base_url}{endpoint}"
        params['apiKey'] = api_key
        
        while True:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Too many requests
                logger.info("Rate limit exceeded. Waiting for 60 seconds...")
                time.sleep(60)
            else:
                logger.error(f"API request failed with status code {response.status_code}")
                raise Exception(f"API request failed with status code {response.status_code}")

    # Get financial data
    financials_endpoint = "/vX/reference/financials"
    financials_params = {
        "ticker": ticker,
        "limit": 10
    }
    financials_data = make_request(financials_endpoint, financials_params)
    
    # Get aggregate (bars) data
    today = datetime.now().date()
    month_ago = today - timedelta(days=30)
    aggs_endpoint = f"/v2/aggs/ticker/{ticker}/range/1/day/{month_ago}/{today}"
    aggs_params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 5000
    }
    aggs_data = make_request(aggs_endpoint, aggs_params)
    
    # Combine the data
    combined_data = {
        "ticker": ticker,
        "financials_data": financials_data,
        "aggregates_data": aggs_data
    }
    
    return combined_data