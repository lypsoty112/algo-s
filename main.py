from src.financial_data import get_financial_data
from src.config import Settings
from src.investor import buy_decision, sell_decision
from src.alpaca import buy_ticker, check_if_tradeable, get_open_postions, sell_ticker
from loguru import logger
from src.analyze_news import analyze_news
from src.get_news import get_news, get_news_ticker
from pymongo import MongoClient
from datetime import datetime

def log_decision(collection, decision_type, ticker, reason):
    decision_log = {
        "type": decision_type,
        "ticker": ticker,
        "reason": reason,
        "timestamp": datetime.now()
    }
    collection.insert_one(decision_log)

def main():
    settings = Settings()
    
    # Set up MongoDB connection
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    decision_collection = db[settings.MONGODB_COLLECTION_NAME]
    
    logger.info("Selling")
    # Get the current postions
    positions = get_open_postions()
    # Iterate over the positions
    position_count = len(positions)
    logger.info(f"Found {position_count} open positions. max: {settings.MAX_STOCKS}")
    for position in positions:
        decision = sell_decision(position, get_news_ticker(position.get('symbol', None)))
        if decision.get('sell', False):
            ticker = position.get('symbol', None)
            reason = decision.get('reasoning', None)
            logger.info(f"Selling {ticker}. Reason: {reason}")
            sell_ticker(ticker)
            log_decision(decision_collection, "sell", ticker, reason)
            position_count -= 1
            
    if position_count >= settings.MAX_STOCKS:
        # Exit here
        logger.info("Cannot invest in new stocks.")
        client.close()
        exit(0)

    logger.info("Getting latest news..")
    news = get_news()
    logger.info("Analysing the results now.")
    worthwhile_news = analyze_news(news)
    logger.info(f"{len(worthwhile_news)} Articles got through analysis.")
    # Get the positions again.
    symbols = [x.get('symbol', None) for x in get_open_postions()]
    symbols.append(None) # Done to remove any unknown tickers
    # Filter any symbol in positions
    worthwhile_news = [x for x in worthwhile_news if x.get('ticker', None) not in symbols]
    for news in worthwhile_news:
        # Check if the ticker is tradeable
        if check_if_tradeable:
            ticker = news.get('ticker', None)
            decision = buy_decision(news, get_news_ticker(ticker), get_financial_data(ticker))
            if decision.get('buy', False):
                reason = decision.get('reasoning', None)
                logger.info(f"Buying {ticker}. Reason: {reason}")
                buy_ticker(ticker)
                log_decision(decision_collection, "buy", ticker, reason)
                position_count += 1

        if position_count == settings.MAX_STOCKS:
            break

    client.close()

if __name__ == "__main__":
    main()