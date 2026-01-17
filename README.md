# Theory Autoencoder

基于大语言模型（LLM）的扎根理论自动化分析工具。本项目通过多阶段的编码流程，实现对文本数据的系统性质性分析。

## 📋 项目概述

扎根理论是一种系统性的质性研究方法论，通过从数据中归纳出理论框架。本项目将扎根理论的经典三阶段编码过程（开放编码、轴心编码、选择性编码）自动化，利用 LLM 的理解和推理能力，高效地处理大规模文本数据。

## 🏗️ 项目结构

```
theory-autoencoder/
├── prompts/                    # 提示词模板
│   ├── 01-information_extraction.txt
│   ├── 02-open_coding.md
│   ├── 03-axial_coding.md
│   ├── 04-selective_coding.txt
│   └── 05-data_saturation_test.txt
├── scripts/
│   ├── generate_input_texts/   # 数据准备脚本
│   │   ├── open_coding.py
│   │   └── axial_coding.py
│   ├── invoke/                 # LLM 调用脚本
│   │   ├── open_coding.py
│   │   └── axial_coding.py
│   └── analyst/                # 结果分析脚本
│       ├── open_coding.py
│       └── axial_coding.py
├── src/
│   └── agent/                  # 核心代理类
│       ├── __init__.py         # BaseAgent 基类
│       └── coding.py           # CodingAgent 实现
├── data/                       # 数据目录
│   ├── raw/                    # 原始数据
│   ├── input_texts/            # 生成的输入文本
│   ├── agents/                 # 代理配置
│   └── tasks/                  # 任务数据
├── logs/                       # 日志文件
└── pyproject.toml             # 项目配置
```

## 🔄 工作流程

### 1. 提示词准备（Prompts）

项目预定义了三个主要编码阶段的提示词：

- **开放式编码**（02-open_coding.md）：识别文本中的初始概念和标签
- **轴心编码**（03-axial_coding.md）：将初始子类别聚合成主要类别
- **TODO: 选择性编码**（04-selective_coding.txt）：识别核心类别并解释其关系
- **TODO: 数据饱和度测试**（05-data_saturation_test.txt）：评估理论饱和度

### 2. 数据准备（Generate Input Texts）

使用 `scripts/generate_input_texts/` 中的脚本将原始数据转换为 LLM 可处理的输入格式。

**示例：开放编码数据准备**

```bash
uv run scripts/generate_input_texts/open_coding.py
```

该脚本会：
- 读取 `prompts/02-open_coding.md` 模板
- 从 `data/raw/` 目录加载原始 JSON 数据
- 将数据填充到提示词模板中
- 生成完整的输入文本列表并保存到 `data/input_texts/open_coding.json`

### 3. LLM 调用（Invoke）

使用 `scripts/invoke/` 中的脚本调用 LLM 执行编码任务。

**示例：执行开放编码**

```bash
uv run python scripts/invoke/open_coding.py
```

该脚本会：
- 加载生成的输入文本
- 创建 OpenCodingAgent 实例
- 为每个输入文本创建任务
- 异步并发执行任务（默认最大并发 20）
- 保存任务状态和结果到磁盘
- 生成执行日志

**核心特性**：
- **任务状态管理**：PENDING、COMPLETED、FAILED
- **并发控制**：使用信号量限制最大并发请求数
- **错误重试**：内置退避机制，连续失败时自动暂停
- **断点续传**：支持从中断的任务继续执行
- **进度跟踪**：使用 tqdm 显示实时进度

### 4. 结果分析（Analyst）

使用 `scripts/analyst/` 中的脚本对编码结果进行深入分析。

**示例：分析开放式编码结果**

```bash
uv run scripts/analyst/open_coding.py
```

或使用 Jupyter Notebook 进行交互式分析：

```bash
scripts/analyst/open-coding.ipynb
```

分析脚本可以：
- 提取和聚合编码标签
- 进行聚类分析（使用 HDBSCAN）
- 可视化编码结果分布
- 生成统计报告

## 🚀 快速开始

### 环境要求

- Python 3.12+
- OpenAI API Key

### 安装依赖

```bash
uv sync
```

### 配置环境变量

创建 `.env` 文件并添加：

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=your_api_base_url
```

### 运行示例

1. **准备数据**

```bash
# 将原始数据放置在 data/raw/ 目录
# 确保数据格式符合脚本要求
uv run scripts/generate_input_texts/open_coding.py
```

2. **执行编码**

```bash
uv run scripts/invoke/open_coding.py
```

3. **分析结果**

```bash
uv run scripts/analyst/open_coding.py
```

## 🧩 核心架构

### BaseAgent 基类

`src/agent/__init__.py` 中的 `BaseAgent` 是所有编码代理的基类，提供：

- **任务管理**：创建、加载、保存任务
- **并发执行**：异步任务调度和执行
- **状态持久化**：Agent 配置和任务状态保存到磁盘
- **日志记录**：详细的执行日志
- **错误处理**：异常捕获和失败重试机制

### 专用代理

- **OpenCodingAgent**：执行开放式编码任务
- **CodingAgent**：通用编码代理
- **AxialCodingAgent**：执行轴心编码任务（可扩展）

### 数据模型

使用 Pydantic 定义的数据模型：

- `AgentConfig`：代理配置
- `TaskSchema`：任务数据结构
- `TasksCreatedResult`：任务创建结果
- `TasksRunningResult`：任务执行结果

## 📊 编码阶段详解

### 第一阶段：开放式编码（Open Coding）

**目标**：识别文本中的概念和现象，为其命名和分类

**输入**：原始文本数据
**输出**：初始概念标签列表
**工具**：`scripts/generate_input_texts/open_coding.py`, `scripts/invoke/open_coding.py`

### 第二阶段：轴心编码（Axial Coding）

**目标**：将开放式编码产生的概念按照其属性和维度重新组合，建立概念之间的联系

**输入**：开放式编码的结果
**输出**：主要类别及其关联的子类别
**工具**：`scripts/generate_input_texts/axial_coding.py`, `scripts/invoke/axial_coding.py`

### 第三阶段：选择性编码（Selective Coding）

**目标**：识别核心类别，建立理论框架

**输入**：轴心编码的结果
**输出**：核心类别及其与其他类别的关系
**工具**：手动或半自动执行

## 🔧 高级功能

### 任务恢复

如果任务执行中断，可以使用相同的 Agent ID 恢复：

```python
agent = OpenCodingAgent(agent_id='your-agent-id')
asyncio.run(agent.run_tasks())
```

### 自定义并发控制

```python
await agent.run_tasks(
    max_concurrent_requests=10,  # 最大并发请求数
    request_gap=0.5              # 请求间隔（秒）
)
```

### 日志查看

日志文件保存在 `logs/` 目录，以 Agent ID 命名：

```bash
tail -f logs/<agent-id>.log
```

## 📚 扩展开发

### 添加新的编码类型

1. 创建新的 Agent 类继承自 `BaseAgent`：

```python
class SelectiveCodingAgent(BaseAgent):
    def __init__(self, agent_id=None, logs_dir=None, data_dir=None):
        super().__init__(
            agent_type=AgentType.SELECTIVE_CODING,
            agent_id=agent_id,
            logs_dir=logs_dir,
            data_dir=data_dir,
        )

    def get_llm(self):
        return ChatOpenAI(model="gpt-4o")
```

2. 在 `AgentType` 枚举中添加新类型：

```python
class AgentType(Enum):
    OPEN_CODING = auto()
    AXIAL_CODING = auto()
    SELECTIVE_CODING = auto()  # 新增
```

3. 创建对应的生成输入文本和调用脚本

## 🛠️ 技术栈

- **Python 3.12+**
- **LangChain**：LLM 应用框架
- **OpenAI GPT-4o-mini**：核心 LLM 模型
- **Pydantic**：数据验证和模型定义
- **asyncio**：异步任务执行
- **HDBSCAN**：聚类分析
- **sentence-transformers**：文本嵌入
- **scikit-learn**：机器学习工具
- **pandas/numpy**：数据处理
- **matplotlib/seaborn**：数据可视化

## 📝 注意事项

1. **API 配额**：大规模数据处理会消耗大量 API 配额，建议先在小规模数据上测试
2. **并发限制**：根据 API 速率限制调整 `max_concurrent_requests` 参数
3. **数据隐私**：确保处理的数据符合隐私保护要求
4. **结果验证**：LLM 编码结果需要人工验证和校准
