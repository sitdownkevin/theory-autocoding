import json
from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI
from src.agent import AgentType, BaseAgent
from json_repair import repair_json


class OpenCodingAgent(BaseAgent):
    def __init__(
        self,
        agent_id: Optional[str] = None,
        logs_dir: Optional[Path] = Path("logs"),
        data_dir: Optional[Path] = Path("data"),
    ) -> None:
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.OPEN_CODING,
            logs_dir=logs_dir,
            data_dir=data_dir,
        )

    def get_llm(self) -> ChatOpenAI:
        return ChatOpenAI(model="gpt-4o-mini")

    
if __name__ == "__main__":
    agent = OpenCodingAgent(agent_id='43d1e949-f2d3-4c4d-b62c-95c81ecf6052')
    print(agent.config.agent_id)

    successful_tasks = agent._get_successful_tasks()
    output_texts = [task.output_text for task in successful_tasks]
    print(output_texts)

    output_texts = [json.loads(repair_json(output_text))['labels'] for output_text in output_texts]
    print(output_texts)
