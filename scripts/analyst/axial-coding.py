import json
from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI
from src.agent import AgentType, BaseAgent
from json_repair import repair_json
from contextlib import suppress

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
    agent = AxialCodingAgent(agent_id='324de497-8e0c-4342-8d3d-0981e508afc8')
    print(agent.config.agent_id)

    successful_tasks = agent._get_successful_tasks()
    output_texts = [task.output_text for task in successful_tasks]
    print(output_texts)

    output_data = []
    for output_text in output_texts:
        with suppress(Exception):
            output_data.append(json.loads(repair_json(output_text)))
    print(output_data)

    Path("data/coding_results").mkdir(parents=True, exist_ok=True)
    with open(Path("data") / "coding_results" / "axial_coding.json", "w") as f:
        json.dump(output_data, f, indent=4)
