import asyncio
from dataclasses import dataclass
import inspect
import json
import logging
import warnings
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from autogen_core import AgentRuntime, AgentType, BaseAgent, CancellationToken, Component, ComponentModel, FunctionCall, MessageContext, Subscription, SubscriptionInstantiationContext, TypePrefixSubscription, default_subscription, message_handler
from autogen_core.memory import Memory
from autogen_core.model_context import (
    ChatCompletionContext,
    UnboundedChatCompletionContext,
)
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    CreateResult,
    FunctionExecutionResult,
    FunctionExecutionResultMessage,
    LLMMessage,
    ModelFamily,
    SystemMessage,
)
from autogen_agentchat.agents import BaseChatAgent, AssistantAgent
from autogen_agentchat.base import Handoff as HandoffBase
from pydantic import BaseModel
from autogen_core.tools import BaseTool, FunctionTool, StaticWorkbench, Workbench
from pydantic import BaseModel
from typing_extensions import Self

from autogenstudio.gallery.agents._types import FinalSolverResponse, SolverRequest


@dataclass
class FinalAnalysisResponse:
    """A dataclass to hold the final analysis response."""
    answer: str


class FundamentalAnalysisAgentConfig(BaseModel):
    """The declarative configuration for the assistant agent."""

    name: str
    model_client: ComponentModel
    tools: List[ComponentModel] | None = None
    workbench: ComponentModel | None = None
    handoffs: List[HandoffBase | str] | None = None
    model_context: ComponentModel | None = None
    memory: List[ComponentModel] | None = None
    description: str
    system_message: str | None = None
    model_client_stream: bool = False
    reflect_on_tool_use: bool
    tool_call_summary_format: str
    metadata: Dict[str, str] | None = None
    structured_message_factory: ComponentModel | None = None


@default_subscription
class FundamentalAnalysisAgent(AssistantAgent, BaseAgent, Component[FundamentalAnalysisAgentConfig]):
    component_config_schema = FundamentalAnalysisAgentConfig
    component_provider_override = "autogenstudio.gallery.agents.fundamental_analysis.FundamentalAnalysisAgent"

    def __init__(
        self,
        name: str,
        model_client: ChatCompletionClient,
        *,
        tools: List[BaseTool[Any, Any] | Callable[..., Any]
                    | Callable[..., Awaitable[Any]]] | None = None,
        workbench: Workbench | None = None,
        handoffs: List[HandoffBase | str] | None = None,
        model_context: ChatCompletionContext | None = None,
        description: str = "An agent that provides assistance with ability to use tools.",
        system_message: (
            str | None
        ) = "You are a helpful AI assistant. Solve tasks using your tools. Reply with TERMINATE when the task has been completed.",
        model_client_stream: bool = False,
        reflect_on_tool_use: bool | None = None,
        tool_call_summary_format: str = "{result}",
        output_content_type: type[BaseModel] | None = None,
        output_content_type_format: str | None = None,
        memory: Sequence[Memory] | None = None,
        metadata: Dict[str, str] | None = None,
        topic_type: str | None = "default",
        max_round: int | None = 3,

    ):
        super().__init__(name=name, description=description,
                         model_client=model_client, tools=tools,
                         workbench=workbench, handoffs=handoffs,
                         model_context=model_context, system_message=system_message,
                         model_client_stream=model_client_stream,
                         reflect_on_tool_use=reflect_on_tool_use,
                         tool_call_summary_format=tool_call_summary_format,
                         output_content_type=output_content_type,
                         output_content_type_format=output_content_type_format,
                         memory=memory, metadata=metadata)
        self._topic_type = topic_type
        self._max_round = max_round

    @message_handler
    async def handle_request(self, message: SolverRequest, ctx: MessageContext) -> None:
        # 运行代理
        task_reulst = await self.run(message.question)

        # 如果不是终止消息，则发布最终响应。
        self._round += 1
        print(task_reulst)
        # if self._round == self._max_round:
        #     # If the counter reaches the maximum round, publishes a final response.
        #     await self.publish_message(
        #         FinalSolverResponse(answer=task_reulst.), topic_id=DefaultTopicId()
        #     )
        # else:
        #     # Publish intermediate response to the topic associated with this solver.
        #     await self.publish_message(
        #         IntermediateSolverResponse(
        #             content=model_result.content,
        #             question=message.question,
        #             answer=answer,
        #             round=self._round,
        #         ),
        #         topic_id=DefaultTopicId(type=self._topic_type),
        #     )
