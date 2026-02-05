import json
from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI
from src.agent import AgentType, BaseAgent
from json_repair import repair_json
from contextlib import suppress

class RelatedAgent(BaseAgent):
    def __init__(
        self,
        agent_id: Optional[str] = None,
        logs_dir: Optional[Path] = Path("logs"),
        data_dir: Optional[Path] = Path("data"),
    ) -> None:
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.RELATED,
            logs_dir=logs_dir,
            data_dir=data_dir,
        )

    def get_llm(self) -> ChatOpenAI:
        return ChatOpenAI(model="gpt-4o")

    
if __name__ == "__main__":
    agent = RelatedAgent(agent_id='944c5ec6-f1da-4261-b484-287c36297dc0')
    print(agent.config.agent_id)

    import re
    
    successful_tasks = agent._get_successful_tasks()
    output_texts = [(task.input_text, task.output_text) for task in successful_tasks]
    print(output_texts)

    output_data = []
    for input_text, output_text in output_texts:
        # 每个 input_text 都有 Subreddit: RooCode 这样的内容，请用正则表达式提取
        with suppress(Exception):
            subreddit_match = re.search(r'- Subreddit: ([^\n]+)', input_text)
            subreddit = subreddit_match.group(1).strip() if subreddit_match else None
            
            parsed_output = json.loads(repair_json(output_text))
            parsed_output['subreddit'] = subreddit
            output_data.append(parsed_output)
    print(output_data)

    Path("data/coding_results").mkdir(parents=True, exist_ok=True)
    with open(Path("data") / "coding_results" / "related.json", "w") as f:
        json.dump(output_data, f, indent=4)
