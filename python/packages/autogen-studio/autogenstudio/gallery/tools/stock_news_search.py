import akshare as ak
from typing import List, Dict, Optional
from autogen_core.code_executor import ImportFromModule
from autogen_core.tools import FunctionTool


async def stock_news_search(
    symbol: str,
) -> List[Dict[str, str]]:
    """
    Fetch stock news information from East Money (东方财富).

    Args:
        symbol: Stock symbol (e.g., "300059")

    Returns:
        List[Dict[str, str]]: List of news articles containing:
            - keyword: Search keyword/stock symbol
            - title: News title
            - content: News content
            - datetime: Publication time
            - source: News source
            - url: News article URL
    """
    try:
        # Fetch data using akshare
        df = ak.stock_news_em(symbol=symbol)

        # Convert DataFrame to list of dictionaries
        results = []
        for _, row in df.iterrows():
            result = {
                "keyword": row.get("关键词", ""),
                "title": row.get("新闻标题", ""),
                "content": row.get("新闻内容", ""),
                "datetime": row.get("发布时间", ""),
                "source": row.get("文章来源", ""),
                "url": row.get("新闻链接", "")
            }
            results.append(result)

        return results

    except Exception as e:
        raise ValueError(f"Error fetching stock news: {str(e)}")

# Create the stock news search tool
stock_news_tool = FunctionTool(
    func=stock_news_search,
    description="""
    Fetch stock news from East Money (东方财富) for a given stock symbol.
    Returns up to 100 most recent news articles with title, content, publication time, source and URL.
    """,
    global_imports=[
        ImportFromModule("typing", ("List", "Dict", "Optional")),
        "akshare",
    ],
)
