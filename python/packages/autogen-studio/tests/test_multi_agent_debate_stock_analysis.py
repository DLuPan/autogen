# 多智能体辩论
import asyncio
import re
from dataclasses import dataclass
from typing import Dict, List

from autogen_core import (
    AgentType,
    DefaultTopicId,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TypeSubscription,
    default_subscription,
    message_handler,
    type_subscription,
)
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    LLMMessage,
    SystemMessage,
    UserMessage,
)
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily

from autogenstudio.gallery.agents._types import Question
from autogenstudio.gallery.agents.fundamental_analysis import FundamentalAnalysisAgent

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

# 构建一个运行时
runtime = SingleThreadedAgentRuntime()


async def main():
    await FundamentalAnalysisAgent.register(
        runtime,
        "FundamentalAnalysisAgentA",
        lambda: FundamentalAnalysisAgent(
            model_client=model_client,
            topic_type="StockAnalysis",
            max_round=3,
        ),
    )

    await FundamentalAnalysisAgent.register(
        runtime,
        "FundamentalAnalysisAgentB",
        lambda: FundamentalAnalysisAgent(
            model_client=model_client,
            topic_type="StockAnalysis",
            max_round=3,
        ),
    )
    # Subscriptions for topic published
    await runtime.add_subscription(TypeSubscription("FundamentalAnalysisAgentA", "FundamentalAnalysisAgentB"))
    await runtime.add_subscription(TypeSubscription("FundamentalAnalysisAgentB", "FundamentalAnalysisAgentA"))
    await runtime.add_subscription(default_subscription())

    question = "分析一下广和通股票"
    runtime.start()
    await runtime.publish_message(Question(content=question), DefaultTopicId())
    # Wait for the runtime to stop when idle.
    await runtime.stop_when_idle()
    # Close the connection to the model client.
    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main=main())
