# 现金流
from typing import Dict, Union
import pandas as pd
from autogen_core.code_executor import ImportFromModule
from autogen_core.tools import FunctionTool


async def get_stock_financial_cash(
    symbol: str = "000063",
    indicator: str = "按报告期"
) -> Dict[str, Union[pd.DataFrame, str]]:
    """
    Get cash flow statement data from THS (同花顺)

    Args:
        symbol: Stock code (e.g., "000063")
        indicator: Report type, one of {"按报告期", "按年度", "按单季度"}

    Returns:
        Dict containing:
            - data: DataFrame with cash flow data (75 metrics)
            - symbol: Stock code used
            - indicator: Report type used
    """
    try:
        # Validate input parameters
        if not isinstance(symbol, str):
            raise ValueError("Symbol must be a string")

        valid_indicators = ["按报告期", "按年度", "按单季度"]
        if indicator not in valid_indicators:
            raise ValueError(f"Indicator must be one of {valid_indicators}")

        # Import akshare within the function to avoid global import issues
        import akshare as ak

        # Get cash flow data using akshare
        df = ak.stock_financial_cash_ths(symbol=symbol, indicator=indicator)

        return {
            "data": df,
            "symbol": symbol,
            "indicator": indicator
        }

    except Exception as e:
        raise ValueError(f"Error getting cash flow data: {str(e)}")

# Create the cash flow tool
cash_flow_tool = FunctionTool(
    func=get_stock_financial_cash,
    description="""
    Get cash flow statement data from THS (同花顺).
    Provides comprehensive cash flow metrics including operating, investing and financing activities.
    Returns DataFrame with 75 financial metrics along with query parameters.
    """,
    global_imports=[
        ImportFromModule("typing", ("Dict", "Union")),
        ImportFromModule("pandas", ("pd",)),
    ],
)
