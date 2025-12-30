import asyncio
from pathlib import Path
from typing import Optional

from langchain_openai import ChatOpenAI
from . import AgentType, BaseAgent


class CodingAgent(BaseAgent):
    def __init__(
        self,
        agent_id: Optional[str] = None,
        logs_dir: Optional[Path] = Path("logs"),
        data_dir: Optional[Path] = Path("data"),
    ) -> None:
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.CODING,
            logs_dir=logs_dir,
            data_dir=data_dir,
        )

    def get_llm(self) -> ChatOpenAI:
        return ChatOpenAI(model="gpt-4o-mini")


if __name__ == "__main__":
    input_texts = [
        "Write a function that adds two numbers",
        "Write a function that multiplies two numbers",
        "Write a function that divides two numbers",
    ]

    agent = CodingAgent()
    print(agent.config.agent_id)

    tasks_created_result = asyncio.run(agent.create_tasks(input_texts))
    print(tasks_created_result)
    tasks_running_result = asyncio.run(agent.run_tasks())
    print(tasks_running_result)

    agent = CodingAgent(
        agent_id=agent.config.agent_id,
    )
    print(agent.config.agent_id)
    print(agent.config.task_ids)
