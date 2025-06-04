import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import StructuredMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from autogen_core.models import UserMessage
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


async def web_search(query: str) -> str:
    """Find information on the web"""
    return "AutoGen is a programming framework for building multi-agent applications."


agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[web_search],
    system_message=system_message,
)


async def main():
    stream = agent.run_stream(task="分析一下广和通")
    await Console(stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
