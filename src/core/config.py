from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)
    ORIGIN: str = Field(alias="ORIGIN")
    NEWS_API_API_KEY: str = Field(alias="NEWS_API_API_KEY")
    OPENAI_API_KEY: str = Field(alias="OPENAI_API_KEY")
    ALPACA_API_KEY: str = Field(alias="ALPACA_API_KEY")
    ALPACA_SECRET_KEY: str = Field(alias="ALPACA_SECRET_KEY")
    PAPER_TRADING: bool = Field(alias="PAPER_TRADING")
    POLYGON_API_KEY: str = Field(alias="POLYGON_API_KEY")

    MAX_STOCKS: int = Field(20, alias="MAX_STOCKS")
    MODEL_NAME: str = Field(alias="MODEL_NAME")
    # MongoDB settings
    UNIQUE_MONGODB_URI: str = Field(alias="UNIQUE_MONGODB_URI")
    MONGODB_DB_NAME: str = Field(alias="MONGODB_DB_NAME")
    MONGODB_COLLECTION_NAME: str = Field(alias="MONGODB_COLLECTION_NAME")

    # App settings yaml file
    APP_SETTINGS_YAML: str = Field(alias="APP_SETTINGS_YAML")


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)

    MAX_PROFIT: float = Field(alias="MAX_PROFIT")
    MAX_LOSS: float = Field(alias="MAX_LOSS")
    MAX_POSITIONS: int = Field(alias="MAX_POSITIONS")
    MAX_DAYS_IN_POSITION: int = Field(alias="MAX_DAYS_IN_POSITION")


settings = Settings()

# Load the yaml file and create the app settings manually
with open(settings.APP_SETTINGS_YAML, "r") as f:
    # Load as a dictionary
    app_settings_dict = yaml.safe_load(f)
    app_settings = AppSettings(**app_settings_dict)
