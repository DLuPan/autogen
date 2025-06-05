import akshare as ak
import pandas as pd

# Configure pandas display options to show all rows and columns
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Auto-detect display width
pd.set_option('display.max_colwidth', None)  # Show full content in each cell


stock_financial_benefit_ths_df = ak.stock_financial_cash_ths(
    symbol="000063", indicator="按报告期")
print(stock_financial_benefit_ths_df.head())
