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


""" 进行多轮辩论的Agent Message Type """


@dataclass
class Question:
    content: str


@dataclass
class Answer:
    content: str


@dataclass
class SolverRequest:
    content: str
    question: str


@dataclass
class IntermediateSolverResponse:
    content: str
    question: str
    answer: str
    round: int


@dataclass
class FinalSolverResponse:
    answer: str

# 构建第一个分析代理，并与其他不同的分析代理进行辩论最终提供


@type_subscription(
    topic_type="stock_analysis"
)
class FundamentalAnalysis(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient, topic_type: str, num_neighbors: int, max_round: int) -> None:
        super().__init__("A debator.")
        self._topic_type = topic_type
        self._model_client = model_client
        self._num_neighbors = num_neighbors
        self._history: List[LLMMessage] = []
        self._buffer: Dict[int, List[IntermediateSolverResponse]] = {}
        self._system_messages = [
            SystemMessage(
                content=(
                    """

你是一位专业的**基本面分析智能体（Fundamental Analysis Agent）**，任务是对指定企业进行多维度、系统化的基本面分析。请依据以下四大模块，结合财务数据、治理结构、行业背景与宏观环境，输出专业、可操作的投资分析报告。

---

## 🧩 分析模块指引：

### 1. 📊 财务报表诊断
- 分析核心财务指标：  
  - 收入增长趋势  
  - 毛利率与净利率  
  - 现金流稳定性（经营/投资/融资）  
  - 资产负债结构  
  - ROE / ROIC  
- 运用杜邦分析法拆解盈利能力  
- 检查潜在财务异常：如收入与现金流背离、存货积压、短期债务压力  
- 进行 3~5 年纵向趋势分析及同行业横向比较

---

### 2. 🏛️ 公司治理与股权结构审计
- 评估董事会独立性、管理层激励机制、内部控制制度透明度  
- 穿透主要股东结构，识别关联交易与利益输送风险  
- 检查 ESG 表现对企业长期可持续性的影响（环境、社会、治理）

---

### 3. 🏹 行业竞争力图谱
- 定量分析目标企业在行业中的市场地位、客户粘性、定价能力  
- 验证其护城河：如技术壁垒、品牌溢价、规模优势、网络效应  
- 运用波特五力模型评估行业进入壁垒与盈利能力  
- 分析供应链集中度与上下游议价能力

---

### 4. 🌏 宏观环境适应性
- 分析企业对政策变化的敏感度（如碳中和、补贴退坡、监管趋严）  
- 结合 PMI、利率、通胀等指标判断行业所处周期  
- 评估地缘政治、汇率波动、全球供应链中断等全球化风险

---

## 📤 输出格式要求（使用以下 Markdown 模板输出）

### 📘 基本面分析报告：{{企业名称}}

#### 📊 一、量化评分卡（0-100 分）

| 分析模块               | 得分 | 简要说明 |
|------------------------|------|----------|
| 财务报表诊断           | {{score_1}} | {{comment_1}} |
| 公司治理与股权结构     | {{score_2}} | {{comment_2}} |
| 行业竞争力图谱         | {{score_3}} | {{comment_3}} |
| 宏观环境适应性         | {{score_4}} | {{comment_4}} |

---

#### 🚨 二、风险预警报告
- **财务异常**：{{财务异常说明}}  
- **治理结构问题**：{{治理结构问题说明}}  
- **行业壁垒变化**：{{竞争壁垒变化说明}}

---

#### 💰 三、价值评估结论
- **估值方法**：{{估值方法}}  
- **核心假设**：  
  - 收入增长率：{{收入增长率}}%  
  - 折现率（WACC）：{{折现率}}%  
  - 永续增长率：{{永续增长率}}%  
- **估值结果**：合理估值区间为 **{{估值下限}} ~ {{估值上限}} 元/股**  
- **当前价格**：{{当前价格}} 元/股  
- **安全边际**：{{安全边际}}%

---

#### 📌 四、投资建议
- **评级**：✅ {{买入 / 持有 / 卖出}}  
- **建议理由**：
  - {{理由1}}  
  - {{理由2}}  
  - {{理由3}}

---

#### 📝 附注
- 报告生成时间：{{报告日期}}  
- 分析来源：基本面分析智能体（Fundamental Analysis Agent）

---

## 🧾 输入数据要求：

请提供以下输入内容（如为结构化 API，可转化为 JSON 格式）：

- 企业名称：{{xxx公司}}  
- 财务报表摘要（最近 3~5 年）  
- 公司治理结构与股权信息  
- 所处行业、主要竞争者情况  
- 宏观/政策环境简况（如有）  
- ESG 报告（如适用）

---

请使用专业语言风格，兼顾逻辑性与可读性，生成一份可供投资机构参考的研究报告。

"""
                )
            )
        ]
        self._round = 0
        self._max_round = max_round

    @message_handler
    async def handle_request(self, message: SolverRequest, ctx: MessageContext) -> None:
        # Add the question to the memory.
        self._history.append(UserMessage(
            content=message.content, source="user"))
        # Make an inference using the model.
        model_result = await self._model_client.create(self._system_messages + self._history)
        assert isinstance(model_result.content, str)
        # Add the response to the memory.
        self._history.append(AssistantMessage(
            content=model_result.content, source=self.metadata["type"]))
        print(
            f"{'-'*80}\nSolver {self.id} round {self._round}:\n{model_result.content}")
        # Extract the answer from the response.
        match = re.search(r"\{\{(\-?\d+(\.\d+)?)\}\}", model_result.content)
        if match is None:
            raise ValueError("The model response does not contain the answer.")
        answer = match.group(1)
        # Increment the counter.
        self._round += 1
        if self._round == self._max_round:
            # If the counter reaches the maximum round, publishes a final response.
            await self.publish_message(FinalSolverResponse(answer=answer), topic_id=DefaultTopicId())
        else:
            # Publish intermediate response to the topic associated with this solver.
            await self.publish_message(
                IntermediateSolverResponse(
                    content=model_result.content,
                    question=message.question,
                    answer=answer,
                    round=self._round,
                ),
                topic_id=DefaultTopicId(type=self._topic_type),
            )

    @message_handler
    async def handle_response(self, message: IntermediateSolverResponse, ctx: MessageContext) -> None:
        # Add neighbor's response to the buffer.
        self._buffer.setdefault(message.round, []).append(message)
        # Check if all neighbors have responded.
        if len(self._buffer[message.round]) == self._num_neighbors:
            print(
                f"{'-'*80}\nSolver {self.id} round {message.round}:\nReceived all responses from {self._num_neighbors} neighbors."
            )
            # Prepare the prompt for the next question.
            prompt = "These are the solutions to the problem from other agents:\n"
            for resp in self._buffer[message.round]:
                prompt += f"One agent solution: {resp.content}\n"
            prompt += (
                "Using the solutions from other agents as additional information, "
                "can you provide your answer to the math problem? "
                f"The original math problem is {message.question}. "
                "Your final answer should be a single numerical number, "
                "in the form of {{answer}}, at the end of your response."
            )
            # Send the question to the agent itself to solve.
            await self.send_message(SolverRequest(content=prompt, question=message.question), self.id)
            # Clear the buffer.
            self._buffer.pop(message.round)
