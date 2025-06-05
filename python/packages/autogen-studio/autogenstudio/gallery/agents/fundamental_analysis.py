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

from autogen_core import AgentRuntime, AgentType, CancellationToken, Component, ComponentModel, FunctionCall, Subscription, SubscriptionInstantiationContext, TypePrefixSubscription
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


class FundamentalAnalysisAgent(AssistantAgent, Component[FundamentalAnalysisAgentConfig]):
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

    @classmethod
    async def register(
        cls,
        runtime: AgentRuntime,
        type: str,
        factory: Callable[[], Self | Awaitable[Self]],
        *,
        skip_class_subscriptions: bool = False,
        skip_direct_message_subscription: bool = False,
    ) -> AgentType:
        agent_type = AgentType(type)
        agent_type = await runtime.register_factory(type=agent_type, agent_factory=factory, expected_class=cls)
        if not skip_class_subscriptions:
            with SubscriptionInstantiationContext.populate_context(agent_type):
                subscriptions: List[Subscription] = []
                for unbound_subscription in cls._unbound_subscriptions():
                    subscriptions_list_result = unbound_subscription()
                    if inspect.isawaitable(subscriptions_list_result):
                        subscriptions_list = await subscriptions_list_result
                    else:
                        subscriptions_list = subscriptions_list_result

                    subscriptions.extend(subscriptions_list)
            for subscription in subscriptions:
                await runtime.add_subscription(subscription)

        if not skip_direct_message_subscription:
            # Additionally adds a special prefix subscription for this agent to receive direct messages
            await runtime.add_subscription(
                TypePrefixSubscription(
                    # The prefix MUST include ":" to avoid collisions with other agents
                    topic_type_prefix=agent_type.type + ":",
                    agent_type=agent_type.type,
                )
            )

        # TODO: deduplication
        for _message_type, serializer in cls._handles_types():
            runtime.add_message_serializer(serializer)

        return agent_type
