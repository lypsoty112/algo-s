


from typing import Dict, List, Literal
from langchain_core.prompts.prompt import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field
from .config import Settings
PROMPT = """
You are tasked with analyzing a news article to determine its impact on businesses. You will be provided with the article's title and description. Your goal is to assess whether the news has an impact on a single business and if that business is mentioned in the article itself.

Here is the article information:

<title>
{title}
</title>

<description>
{description}
</description>

Please follow these steps:

1. Carefully read the article title and description.

2. Analyze the content to determine if the news has a significant impact on any business. Consider the following:
   - Does the article discuss changes, events, or developments that could affect a company's operations, finances, or reputation?
   - Is there a clear focus on a particular industry or sector?

3. If you identify that the news impacts a business, determine if it's a single business or multiple businesses.

4. If a single business is impacted, check if that specific business is explicitly mentioned in the article title or description.

5. Provide your reasoning for your conclusions. Consider the following in your analysis:
   - What evidence in the article supports your conclusion?
   - If a single business is impacted, explain why you believe it's only one business and not multiple.
   - If the impacted business is mentioned, quote the relevant part of the article.

6. Based on your analysis, provide a "yes" or "no" answer to the question: "Does the news of this article have an impact on a single business, and is that business mentioned in the article itself?"

7. Format your response according to the following instructions:
{format_instructions}

Remember to provide clear and concise reasoning for your conclusions, and ensure your response adheres to the specified format.
"""

settings = Settings()

class Response(BaseModel):
    reasoning: str
    impacts_a_single_mentioned_business: Literal["yes", "no"]
    is_public: Literal["yes", "no"] = Field("Whether or not the company discussed is a public company.")
    ticker: str = Field("The stock's ticker")

output_parser = PydanticOutputParser(pydantic_object=Response)


prompt = PromptTemplate.from_template(template=PROMPT, partial_variables={"format_instructions": output_parser.get_format_instructions()})
llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)

chain = prompt | llm | output_parser

def analyze_news(news:List[Dict]):

    ret = []
    for article in news:
        # Find the title & description.
        try:
            assert "title" in article
            assert "description" in article
            assert "content" in article
            result: Response = chain.invoke({
                "title": article["title"],
                "description": article["description"]
            })

            if result.impacts_a_single_mentioned_business.lower() == "yes" and result.is_public.lower() == "yes" :
                # Log & add
                article["reasoning"] = result.reasoning
                article["ticker"] = result.ticker
                logger.info(f"Adding business {article['ticker']}. Reasoning: {result.reasoning}")
                ret.append(article)
                if len(ret) >= settings.MAX_STOCKS:
                    return ret

        except AssertionError as e:
            logger.info(f"Passing article, error: {str(e)}")

        except Exception as e:
            logger.exception(e)

    return ret