

from datetime import datetime
from typing import List, Literal
from pymongo import MongoClient
from src.config import Settings
from loguru import logger


settings = Settings()

# Set up MongoDB connection
logger.info(f"Connecting to db: {settings.UNIQUE_MONGODB_URI}")
client = MongoClient(settings.UNIQUE_MONGODB_URI)
db = client[settings.MONGODB_DB_NAME]
decision_collection = db[settings.MONGODB_COLLECTION_NAME]



def log_decision(ticker: str, 
                 reason: str, 
                 action: Literal['buy', "don't buy", "sell", "don't sell", "add to list", "don't add to list"],
                 provided_data: dict = None):
    # TODO: Add tries here
    decision_log = {
        "action": action,
        "ticker": ticker,
        "reason": reason,
        "data": provided_data,
        "timestamp": datetime.now()
    }
    decision_collection.insert_one(decision_log)
    logger.info("Added 1 record to db")

def log_multiple(data: List[dict]):
    # TODO: Same
    decision_logs = [
        {
            **x,
            "timestamp": datetime.now()
        } for x in data
    ]
    # Assert each decision log contains the correct data
    assert all([
        "action" in x and "ticker" in x and "reason" in x and "data" in x
        for x in decision_logs
    ])
    decision_collection.insert_many(decision_logs)
    logger.info(f"Added {len(decision_logs)} record(s) to db")


def close_db():
    client.close()