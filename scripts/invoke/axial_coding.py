import asyncio
import json
from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI
from src.agent import AgentType, BaseAgent


class AxialCodingAgent(BaseAgent):
    def __init__(
        self,
        agent_id: Optional[str] = None,
        logs_dir: Optional[Path] = Path("logs"),
        data_dir: Optional[Path] = Path("data"),
    ) -> None:
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.AXIAL_CODING,
            logs_dir=logs_dir,
            data_dir=data_dir,
        )

    def get_llm(self) -> ChatOpenAI:
        return ChatOpenAI(model="gpt-4o")


if __name__ == "__main__":
    with open(Path("data") / "input_texts" / "axial_coding.json", "r") as f:
        input_texts = json.load(f)

    input_texts = input_texts[:2]

    agent = AxialCodingAgent()
    print(agent.config.agent_id)

    tasks_created_result = asyncio.run(agent.create_tasks(input_texts))
    print(tasks_created_result)

    tasks_running_result = asyncio.run(agent.run_tasks())
    print(tasks_running_result)

