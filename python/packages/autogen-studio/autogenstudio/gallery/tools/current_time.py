from datetime import datetime
from typing import Dict, Optional
from zoneinfo import ZoneInfo
from autogen_core.code_executor import ImportFromModule
from autogen_core.tools import FunctionTool


async def get_current_time(
    timezone: str = "Asia/Shanghai",
    format: str = "YYYY-MM-DD HH:mm:ss"
) -> Dict[str, str]:
    """
    Get current time in specified timezone and format.

    Args:
        timezone: Timezone name (e.g., "Asia/Shanghai", "UTC", "America/New_York")
        format: Output format string, supports:
               - "YYYY-MM-DD HH:mm:ss" (default)
               - "YYYY-MM-DD"
               - "HH:mm:ss"
               - "timestamp" (Unix timestamp)

    Returns:
        Dict containing:
            - datetime: Formatted datetime string
            - timezone: Timezone used
            - timestamp: Unix timestamp
    """
    try:
        # Get current time in specified timezone
        current_time = datetime.now(ZoneInfo(timezone))

        # Format the time according to specified format
        if format == "YYYY-MM-DD HH:mm:ss":
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        elif format == "YYYY-MM-DD":
            formatted_time = current_time.strftime("%Y-%m-%d")
        elif format == "HH:mm:ss":
            formatted_time = current_time.strftime("%H:%M:%S")
        elif format == "timestamp":
            formatted_time = str(int(current_time.timestamp()))
        else:
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        return {
            "datetime": formatted_time,
            "timezone": timezone,
            "timestamp": str(int(current_time.timestamp()))
        }

    except Exception as e:
        raise ValueError(f"Error getting current time: {str(e)}")

# Create the time tool
current_time_tool = FunctionTool(
    func=get_current_time,
    description="""
    Get current time in specified timezone and format.
    Supports multiple timezones and output formats.
    Returns formatted datetime string, timezone, and Unix timestamp.
    """,
    global_imports=[
        ImportFromModule("datetime", ("datetime",)),
        ImportFromModule("typing", ("Dict", "Optional")),
        ImportFromModule("zoneinfo", ("ZoneInfo",)),
    ],
)
