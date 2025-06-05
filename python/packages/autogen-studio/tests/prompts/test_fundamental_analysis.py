import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import StructuredMessage
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from autogen_core.models import UserMessage

from autogenstudio.gallery.tools import current_time, stock_balance_sheet, stock_benefit_statement_data, stock_cash_flow, stock_financial_indicators, stock_news_search, stock_zyjs
import logging

from autogen_agentchat import EVENT_LOGGER_NAME, TRACE_LOGGER_NAME

logging.basicConfig(level=logging.WARNING)

# For trace logging.
trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
trace_logger.addHandler(logging.StreamHandler())
trace_logger.setLevel(logging.DEBUG)

# For structured message logging, such as low-level messages between agents.
event_logger = logging.getLogger(EVENT_LOGGER_NAME)
event_logger.addHandler(logging.StreamHandler())
event_logger.setLevel(logging.DEBUG)
# 准备需要使用得模型
model_client = model_client = OpenAIChatCompletionClient(
    model="deepseek-chat",
    api_key="sk-598569c544c24182a7e42e939a58ae22",
    base_url="https://api.deepseek.com/v1",
    model_info={
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "family": ModelFamily.UNKNOWN,
            "structured_output": True,
    },
)

# Read system message from file
current_dir = os.path.dirname(os.path.abspath(__file__))
system_message_path = os.path.join(current_dir, 'fundamental_analysis_v_1.txt')

with open(system_message_path, 'r', encoding='utf-8') as f:
    system_message = f.read()


agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[stock_zyjs.stock_zyjs_tool,
           current_time.current_time_tool,
           stock_financial_indicators.stock_financial_indicators_tool,
           stock_balance_sheet.balance_sheet_tool,
           stock_cash_flow.cash_flow_tool,
           stock_news_search.stock_news_tool,
           stock_benefit_statement_data.benefit_statement_data_tool
           ],
    system_message=system_message,
)

# Termination condition that stops the task if the agent responds with a text message.
termination_condition = TextMessageTermination("agent")

# Create a team with the looped assistant agent and the termination condition.
team = RoundRobinGroupChat(
    [agent],
    termination_condition=termination_condition,
)


async def main():
    stream = team.run_stream(task="分析一下润建股份")
    await Console(stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
