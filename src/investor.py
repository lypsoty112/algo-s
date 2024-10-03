
from typing import Literal
from pydantic import BaseModel
from src.config import Settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts.prompt import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import src.database as db


settings = Settings()
BUY_PROMPT = """
You are a financial analyst tasked with providing investment advice based on recent news and financial data. Your goal is to decide whether it's advisable to buy a specific stock with a short-term investment horizon of 2 months or less.

First, carefully review the following information:

<news>
{news}
</news>

<financial_data>
{financial_data}
</financial_data>

Your task is to analyze this information and decide whether it's advisable to buy stock in {ticker} now, with the intention of selling within 2 months or less.

To make this decision, consider the following factors:
1. The impact of the recent news on the company's short-term prospects
2. Current financial metrics and how they compare to industry standards
3. Recent stock price movements and trading volume
4. Any upcoming events or announcements that could affect the stock price
5. Overall market conditions and sector trends

In your analysis, be sure to:
- Identify key positive and negative factors that could influence the stock price in the short term
- Assess the potential risks and rewards of investing in this stock
- Consider the likelihood of the stock price increasing within the 2-month time frame

Based on your analysis, make a final recommendation on wether to buy this stock or not.
{format_instructions}
"""

SELL_PROMPT = """
You are a financial analyst tasked with making a recommendation on whether to sell a particular stock. You will be provided with recent news, financial data, and other relevant information about the stock. Your goal is to analyze this information and decide whether the stock should be sold right now.

First, review the recent news related to the company and its industry:

<news>
{news}
</news>

Next, examine the financial data for the stock:

<financial_data>
{financial_data}
</financial_data>

Now, consider the following information:
- The stock ticker symbol is {ticker}
- The current position has changed by {pct_change} percent
- Selling now would be {is_profitable}

Analyze the provided information carefully. Consider the following factors in your analysis:
1. Recent news and its potential impact on the stock price
2. Financial indicators and their trends
3. The overall market conditions
4. The time since the stock was purchased
5. The current profitability of the position

Based on your analysis, determine whether the stock should be sold right now. Provide a detailed reasoning for your decision, considering both the potential upsides and downsides of selling or holding the stock.

After your analysis, make a clear recommendation on wether to sell: 'yes' or 'no'.

Present your reasoning as well.

{format_instructions}
Ensure that your analysis is thorough, your recommendation is clear, and your confidence score accurately reflects the strength of your conviction based on the available information.
"""


llm = ChatOpenAI(model=settings.MODEL_NAME, api_key=settings.OPENAI_API_KEY)

class BuyResponse(BaseModel):
    reasoning: str = "Your reasoning, short & consise. Written on 1 line."
    buy: Literal['yes', 'no']

class SellResponse(BaseModel):
    reasoning: str = "Your reasoning, short & consise. Written on 1 line."
    sell: Literal['yes', 'no']

sell_outputParser = PydanticOutputParser(pydantic_object=SellResponse)
buy_outputParser = PydanticOutputParser(pydantic_object=BuyResponse)


sell_prompt = PromptTemplate.from_template(template=SELL_PROMPT, partial_variables={"format_instructions": sell_outputParser.get_format_instructions()})
buy_prompt = PromptTemplate.from_template(template=BUY_PROMPT, partial_variables={"format_instructions": buy_outputParser.get_format_instructions()})

sell_chain = sell_prompt | llm | sell_outputParser
buy_chain = buy_prompt | llm | buy_outputParser

def buy_decision(trigger:dict, news:dict, financial_data: dict) -> dict:
    ticker = trigger.get('ticker', None)
    input_data = {
        'news': str(news),
        'financial_data': str(financial_data),
        'ticker': ticker
    }

    response: BuyResponse = buy_chain.invoke(input_data)

    # Add to db
    db.log_decision(
        ticker,
        response.reasoning,
        "buy" if response.buy.lower() == 'yes' else "don't buy",
        {
            "input_data": input_data,
            "output_data": response.model_dump()
        }
    )


    return {
        'reasoning': response.reasoning,
        'buy': response.buy.lower() == 'yes'
    }


def sell_decision(position: dict, news: dict, financial_data: dict) -> dict: 
    profit = position.get('unrealized_plpc', None)
    is_profitable = False
    if profit is not None:
        profit = float(profit) * 100
        is_profitable = profit > 0
    
    ticker = position.get('symbol', None)
    input_data = {
        'news': str(news),
        'financial_data': str(financial_data),
        'ticker': ticker,
        'pct_change': profit,
        'is_profitable': is_profitable
    }

    response: SellResponse = sell_chain.invoke(
        input_data
    )

    db.log_decision(
        ticker,
        response.reasoning,
        "sell" if response.sell.lower() == 'yes' else "don't sell",
        {
            "input_data": input_data,
            "output_data": response.model_dump()
        }
    )


    return {
        'reasoning': response.reasoning,
        'sell': response.sell.lower() == 'yes'
    }