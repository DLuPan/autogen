from typing import Dict
import akshare as ak
from autogen_core.tools import FunctionTool
from autogen_core.code_executor import ImportFromModule


async def stock_zyjs(symbol: str) -> Dict:
    """
    Fetch stock main business information from Tonghuashun (同花顺).

    Args:
        symbol: Stock symbol (e.g., "000066")

    Returns:
        Dict: Stock information including main business, product type, product name, and business scope
    """
    try:
        # Fetch data using akshare
        df = ak.stock_zyjs_ths(symbol=symbol)

        if not df.empty:
            # Convert the first row to a dictionary
            result = df.iloc[0].to_dict()
            return {
                "股票代码": result.get("股票代码", ""),
                "主营业务": result.get("主营业务", ""),
                "产品类型": result.get("产品类型", ""),
                "产品名称": result.get("产品名称", ""),
                "经营范围": result.get("经营范围", "")
            }
        return {}
    except Exception as e:
        return {"error": str(e)}

# Create the stock information tool
stock_zyjs_tool = FunctionTool(
    func=stock_zyjs,
    description="Fetch stock main business information from Tonghuashun (同花顺)",
    global_imports=[
        ImportFromModule("typing", ("Dict",)),
        "akshare",
    ],
)
