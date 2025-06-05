import akshare as ak
from typing import Dict, List, Optional
from autogen_core.code_executor import ImportFromModule
from autogen_core.tools import FunctionTool
import pandas as pd


async def fetch_financial_indicators(
    symbol: str,
    start_year: str,
) -> Dict:
    """
    Fetch financial analysis indicators from Sina Finance.

    Args:
        symbol: Stock symbol (e.g., "600004")
        start_year: Starting year for data query (e.g., "2020")

    Returns:
        Dict: Financial indicators containing detailed metrics grouped by category
    """
    try:
        # Fetch data using akshare
        df = ak.stock_financial_analysis_indicator(
            symbol=symbol, start_year=start_year)

        # Convert DataFrame to list of dictionaries with more readable format
        results = []
        for _, row in df.iterrows():
            # Convert row to dictionary and handle NaN values
            row_dict = row.where(pd.notnull(row), None).to_dict()

            # Add formatted result with comprehensive metrics
            result = {
                "date": row_dict.get("日期"),
                "financial_metrics": {
                    "per_share_indicators": {
                        "eps_basic": row_dict.get("摊薄每股收益(元)"),
                        "eps_diluted": row_dict.get("加权每股收益(元)"),
                        "eps_adjusted": row_dict.get("每股收益_调整后(元)"),
                        "eps_excl_extraordinary": row_dict.get("扣除非经常性损益后的每股收益(元)"),
                        "nav_pre_adjustment": row_dict.get("每股净资产_调整前(元)"),
                        "nav_post_adjustment": row_dict.get("每股净资产_调整后(元)"),
                        "operating_cash_flow": row_dict.get("每股经营性现金流(元)"),
                        "capital_reserve": row_dict.get("每股资本公积金(元)"),
                        "retained_earnings": row_dict.get("每股未分配利润(元)"),
                        "nav_adjusted": row_dict.get("调整后的每股净资产(元)")
                    },
                    "profitability": {
                        "total_asset_profit_ratio": row_dict.get("总资产利润率(%)"),
                        "operating_profit_ratio": row_dict.get("主营业务利润率(%)"),
                        "net_asset_profit_ratio": row_dict.get("总资产净利润率(%)"),
                        "cost_expense_profit_ratio": row_dict.get("成本费用利润率(%)"),
                        "operating_margin": row_dict.get("营业利润率(%)"),
                        "main_business_cost_ratio": row_dict.get("主营业务成本率(%)"),
                        "net_profit_margin": row_dict.get("销售净利率(%)"),
                        "roe": row_dict.get("净资产收益率(%)"),
                        "weighted_roe": row_dict.get("加权净资产收益率(%)"),
                        "gross_profit_margin": row_dict.get("销售毛利率(%)")
                    },
                    "growth": {
                        "revenue_growth": row_dict.get("主营业务收入增长率(%)"),
                        "net_profit_growth": row_dict.get("净利润增长率(%)"),
                        "net_asset_growth": row_dict.get("净资产增长率(%)"),
                        "total_asset_growth": row_dict.get("总资产增长率(%)")
                    },
                    "operational_efficiency": {
                        "accounts_receivable_turnover": row_dict.get("应收账款周转率(次)"),
                        "accounts_receivable_days": row_dict.get("应收账款周转天数(天)"),
                        "inventory_turnover": row_dict.get("存货周转率(次)"),
                        "inventory_days": row_dict.get("存货周转天数(天)"),
                        "fixed_asset_turnover": row_dict.get("固定资产周转率(次)"),
                        "total_asset_turnover": row_dict.get("总资产周转率(次)"),
                        "total_asset_days": row_dict.get("总资产周转天数(天)")
                    },
                    "financial_stability": {
                        "current_ratio": row_dict.get("流动比率"),
                        "quick_ratio": row_dict.get("速动比率"),
                        "cash_ratio": row_dict.get("现金比率(%)"),
                        "interest_coverage": row_dict.get("利息支付倍数"),
                        "debt_ratio": row_dict.get("资产负债率(%)"),
                        "equity_ratio": row_dict.get("股东权益比率(%)")
                    },
                    "investment_metrics": {
                        "short_term_investments": {
                            "stocks": row_dict.get("短期股票投资(元)"),
                            "bonds": row_dict.get("短期债券投资(元)"),
                            "other": row_dict.get("短期其它经营性投资(元)")
                        },
                        "long_term_investments": {
                            "stocks": row_dict.get("长期股票投资(元)"),
                            "bonds": row_dict.get("长期债券投资(元)"),
                            "other": row_dict.get("长期其它经营性投资(元)")
                        }
                    },
                    "receivables_aging": {
                        "accounts_receivable": {
                            "within_1year": row_dict.get("1年以内应收帐款(元)"),
                            "1_2_years": row_dict.get("1-2年以内应收帐款(元)"),
                            "2_3_years": row_dict.get("2-3年以内应收帐款(元)"),
                            "within_3years": row_dict.get("3年以内应收帐款(元)")
                        },
                        "prepayments": {
                            "within_1year": row_dict.get("1年以内预付货款(元)"),
                            "1_2_years": row_dict.get("1-2年以内预付货款(元)"),
                            "2_3_years": row_dict.get("2-3年以内预付货款(元)"),
                            "within_3years": row_dict.get("3年以内预付货款(元)")
                        },
                        "other_receivables": {
                            "within_1year": row_dict.get("1年以内其它应收款(元)"),
                            "1_2_years": row_dict.get("1-2年以内其它应收款(元)"),
                            "2_3_years": row_dict.get("2-3年以内其它应收款(元)"),
                            "within_3years": row_dict.get("3年以内其它应收款(元)")
                        }
                    }
                }
            }
            results.append(result)

        return {
            "symbol": symbol,
            "start_year": start_year,
            "indicators": results
        }

    except Exception as e:
        raise ValueError(f"Error fetching financial indicators: {str(e)}")

# Create the financial indicators tool
stock_financial_indicators_tool = FunctionTool(
    func=fetch_financial_indicators,
    description="""
    Fetch comprehensive financial analysis indicators from Sina Finance for a given stock symbol and start year.
    Returns detailed metrics including:
    - Per share indicators (EPS, NAV, etc.)
    - Profitability metrics (ROE, margins, etc.)
    - Growth metrics (revenue, profit growth, etc.)
    - Operational efficiency (turnover ratios)
    - Financial stability (liquidity ratios)
    - Investment metrics
    - Receivables aging analysis
    """,
    global_imports=[
        ImportFromModule("typing", ("Dict", "List", "Optional")),
        "akshare",
        "pandas",
    ],
)
