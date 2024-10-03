import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)
    ORIGIN: str = Field(alias="ORIGIN")
    NEWS_API_API_KEY: str = Field(alias="NEWS_API_API_KEY")
    OPENAI_API_KEY: str = Field(alias="OPENAI_API_KEY")
    ALPACA_API_KEY: str = Field(alias="ALPACA_API_KEY")
    ALPACA_SECRET_KEY: str = Field(alias="ALPACA_SECRET_KEY")
    POLYGON_API_KEY: str = Field(alias="POLYGON_API_KEY")

    MAX_STOCKS: int = Field(20, alias="MAX_STOCKS")
    MODEL_NAME: str = Field(alias="MODEL_NAME")
    # MongoDB settings
    UNIQUE_MONGODB_URI: str = Field(alias="UNIQUE_MONGODB_URI")
    MONGODB_DB_NAME: str = Field(alias="MONGODB_DB_NAME")
    MONGODB_COLLECTION_NAME: str = Field(alias="MONGODB_COLLECTION_NAME")