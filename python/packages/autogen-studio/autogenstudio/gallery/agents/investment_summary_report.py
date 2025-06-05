

import asyncio
from dataclasses import dataclass
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

from autogen_core import (CancellationToken, Component, ComponentModel, FunctionCall, MessageContext,
                          default_subscription,
                          message_handler,
                          type_subscription,)
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

from tests.test_multi_agent_debate_stock_analysis import IntermediateSolverResponse, Question


class InvestmentSummaryReportAgentConfig(BaseModel):
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


class InvestmentSummaryReportAgent(AssistantAgent, Component[InvestmentSummaryReportAgentConfig]):
    """An agent that provides assistance with ability to use tools."""
    component_config_schema = InvestmentSummaryReportAgentConfig
    component_provider_override = "autogenstudio.gallery.agents.investment_summary_report.InvestmentSummaryReportAgent"

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
        num_analysis: int | None = None,
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
        self._num_analysis = num_analysis

    @message_handler
    async def handle_question(self, message: Question, ctx: MessageContext) -> None:
        """ 处理用户请求 """
        self.on_messages()
        pass

    @message_handler
    async def handle_response(self, message: IntermediateSolverResponse, ctx: MessageContext) -> None:
        """ 处理中间结果 """
        pass
