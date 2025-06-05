import akshare as ak
from typing import Dict, Optional, List, Union
import pandas as pd
from autogen_core.tools import FunctionTool
from autogen_core.code_executor import ImportFromModule


async def get_stock_financial_benefit(
    symbol: str = "000063",
    indicator: str = "按报告期"
) -> Dict[str, Union[pd.DataFrame, str]]:
    """
    Get financial benefit statement data from THS (同花顺)

    Args:
        symbol: Stock code (e.g., "000063")
        indicator: Report type, one of {"按报告期", "按年度", "按单季度"}

    Returns:
        Dict containing:
            - data: DataFrame with financial benefit data
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

        # Get financial data using akshare
        df = ak.stock_financial_benefit_ths(symbol=symbol, indicator=indicator)

        return {
            "data": df,
            "symbol": symbol,
            "indicator": indicator
        }

    except Exception as e:
        raise ValueError(f"Error getting financial data: {str(e)}")

# Create the financial benefit tool
benefit_statement_data_tool = FunctionTool(
    func=get_stock_financial_benefit,
    description="""
    Get financial benefit statement data from THS (同花顺).
    Provides comprehensive financial indicators including net profit, revenue, costs etc.
    Returns DataFrame with 45 financial metrics along with query parameters.
    """,
    global_imports=[
        ImportFromModule("akshare", ("ak",)),
        ImportFromModule("typing", ("Dict", "Optional", "List", "Union")),
        ImportFromModule("pandas", ("pd",)),
    ],
)
