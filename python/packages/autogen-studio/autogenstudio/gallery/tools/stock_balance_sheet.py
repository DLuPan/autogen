from typing import Dict, List, Optional
import akshare as ak
import pandas as pd
from autogen_core.code_executor import ImportFromModule
from autogen_core.tools import FunctionTool


async def get_balance_sheet(
    symbol: str,
    report_type: str = "按年度",
    num_periods: Optional[int] = 5,
    include_full_data: bool = False
) -> Dict[str, List]:
    """
    Fetch balance sheet data from THS (同花顺) financial database.

    Args:
        symbol: Stock symbol (e.g., "000063")
        report_type: Report type, options: "按报告期", "按年度", "按单季度"
        num_periods: Number of periods to return (default: 5, None for all)
        include_full_data: Whether to include all available metrics (default: False)

    Returns:
        Dict containing:
            - periods: List of reporting periods
            - core_metrics: Dict of core financial metrics including:
                - total_equity: Total shareholder equity
                - total_assets: Total assets
                - total_liabilities: Total liabilities
                - current_assets: Total current assets
                - non_current_assets: Total non-current assets
                - current_liabilities: Total current liabilities
                - non_current_liabilities: Total non-current liabilities
            - full_data: Complete balance sheet data if include_full_data=True
    """
    try:
        # Fetch data using AKShare
        df = ak.stock_financial_debt_ths(symbol=symbol, indicator=report_type)

        def convert_amount(value: str) -> float:
            """Convert Chinese number format to float"""
            try:
                if isinstance(value, str):
                    if '亿' in value:
                        return float(value.replace('亿', '')) * 100000000
                    elif '万' in value:
                        return float(value.replace('万', '')) * 10000
                return float(value) if value is not False else 0.0
            except:
                return 0.0

        # Limit number of periods if specified
        if num_periods:
            df = df.head(num_periods)

        # Extract periods
        periods = df['报告期'].tolist()

        # Extract core metrics
        core_metrics = {
            "total_equity": [convert_amount(x) for x in df['所有者权益（或股东权益）合计'].tolist()],
            "total_assets": [convert_amount(x) for x in df['资产合计'].tolist()],
            "total_liabilities": [convert_amount(x) for x in df['负债合计'].tolist()],
            "current_assets": [convert_amount(x) for x in df['流动资产合计'].tolist()],
            "non_current_assets": [convert_amount(x) for x in df['非流动资产合计'].tolist()],
            "current_liabilities": [convert_amount(x) for x in df['流动负债合计'].tolist()],
            "non_current_liabilities": [convert_amount(x) for x in df['非流动负债合计'].tolist()]
        }

        result = {
            "symbol": symbol,
            "report_type": report_type,
            "periods": periods,
            "core_metrics": core_metrics
        }

        # Include full data if requested
        if include_full_data:
            full_data = {}
            for column in df.columns:
                if column != '报告期':
                    full_data[column] = [convert_amount(
                        x) for x in df[column].tolist()]
            result["full_data"] = full_data

        return result

    except Exception as e:
        raise ValueError(f"Error fetching balance sheet data: {str(e)}")


# Create the balance sheet tool
balance_sheet_tool = FunctionTool(
    func=get_balance_sheet,
    description="""
    Fetch balance sheet data from THS (同花顺) financial database.
    Returns key financial metrics including total equity, assets, and liabilities.
    Supports different report types and configurable number of periods.
    Can return full detailed balance sheet data if requested.
    """,
    global_imports=[
        ImportFromModule("typing", ("Dict", "List", "Optional")),
        "akshare as ak",
        "pandas as pd"
    ],
)
