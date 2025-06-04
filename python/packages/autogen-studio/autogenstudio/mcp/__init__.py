# 初始化所有的mcp服务


from fastapi import FastAPI
from fastapi_mcp import FastApiMCP


def stock_mcp_services(app: FastAPI):
    # Create your FastMCP server as well as any tools, resources, etc.
    stock_mcp = FastApiMCP(app, name="stock_mcp", include_tags=["stock"])
    stock_mcp.mount(mount_path="/mcp-server/stock")


def initialize_mcp_services(app: FastAPI):
    # Initialize all MCP services
    # This function should be called during application startup
    # to ensure all services are ready to handle requests.
    stock_mcp_services(app)
