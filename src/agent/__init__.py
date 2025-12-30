import uuid
import asyncio
from collections import deque
from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from tqdm import tqdm
from langchain_openai import ChatOpenAI

_ = load_dotenv(find_dotenv())


class AgentType(Enum):
    OPEN_CODING = auto()
    AXIAL_CODING = auto()


class AgentConfig(BaseModel):
    agent_type: AgentType
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_ids: Optional[list[str]] = None


class TaskStatus(Enum):
    PENDING = auto()
    COMPLETED = auto()
    FAILED = auto()


class TaskSchema(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    input_text: str
    output_text: Optional[str] = None


class TasksCreatedResult(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    num_tasks_created: int = Field(default=0)


class TasksRunningResult(BaseModel):
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    num_tasks_started: int = Field(default=0)
    num_tasks_completed: int = Field(default=0)
    num_tasks_failed: int = Field(default=0)
    num_tasks_skipped: int = Field(default=0)


class BaseAgent(ABC):
    def __init__(
        self,
        agent_type: AgentType,
        agent_id: Optional[str] = None,
        data_dir: Path = Path("data"),
        logs_dir: Path = Path("logs"),
    ) -> None:
        self.data_dir = data_dir
        self.logs_dir = logs_dir

        if agent_id is None:  # If no agent ID is provided, generate a new one
            agent_id = str(uuid.uuid4())

            # Create a new agent config
            self.config = AgentConfig(
                agent_type=agent_type,
                task_ids=None,
            )

            # Save the agent config to disk
            self._save_agent_config_to_disk()  # Save the agent config to disk
        else:  # If an agent ID is provided, load the agent config from disk
            self.config = self._load_agent_config_from_disk(
                agent_id
            )  # Load the agent config from disk

    @abstractmethod
    def get_llm(self) -> ChatOpenAI: ...

    async def create_tasks(self, input_texts: list[str]) -> TasksCreatedResult:
        # Create a new task for each input text
        tasks = [TaskSchema(input_text=input_text) for input_text in input_texts]
        # Save the tasks to disk
        for task in tasks:
            # Save the task to disk
            self._save_task_to_disk(task)
        # Update the agent config with the new task IDs
        self.config.task_ids = [task.task_id for task in tasks]
        # Save the agent config to disk
        self._save_agent_config_to_disk()
        # Return the number of tasks created
        return TasksCreatedResult(num_tasks_created=len(tasks))

    async def run_task(self, task: TaskSchema) -> TaskSchema:
        # Skip execution if already completed
        if task.status == TaskStatus.COMPLETED:
            self._log(
                f"Task {task.task_id} already completed. Skipping execution.",
                level="info",
            )
            return task

        llm = self.get_llm()

        try:
            response = await llm.ainvoke(f"{task.input_text}")
            output_text = getattr(response, "content", str(response))
            task_completed = TaskSchema(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                input_text=task.input_text,
                output_text=output_text,
            )
            self._save_task_to_disk(task_completed)
            self._log(
                f"Task {task_completed.task_id} completed successfully.", level="info"
            )
            return task_completed
        except Exception as exc:
            failed_task = TaskSchema(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                input_text=task.input_text,
                output_text=str(exc),
            )
            # Persist failed state for visibility
            self._save_task_to_disk(failed_task)
            self._log(f"Task {failed_task.task_id} failed: {str(exc)}", level="error")
            return failed_task

    async def run_tasks(
        self, max_concurrent_requests: int = 20, request_gap: float = 0.2
    ) -> TasksRunningResult:
        tasks_running_result = TasksRunningResult()

        if not self.config.task_ids:
            return tasks_running_result

        semaphore = asyncio.Semaphore(
            max_concurrent_requests
        )  # Limit concurrent network calls
        progress = tqdm(
            total=len(self.config.task_ids), desc="Running tasks", unit="task"
        )
        current_requests = 0
        counter_lock = asyncio.Lock()
        failure_times = deque()
        failure_lock = asyncio.Lock()
        backoff_event = asyncio.Event()
        backoff_event.set()
        backoff_in_progress = False
        failure_threshold = 3
        failure_window_secs = 60
        backoff_sleep_secs = 5

        async def _update_inflight(delta: int) -> None:
            nonlocal current_requests
            async with counter_lock:
                current_requests += delta
                progress.set_postfix({"inflight": current_requests})

        async def _handle_failure_backoff(task_id: str) -> None:
            nonlocal backoff_in_progress
            now = datetime.now()
            need_backoff = False

            async with failure_lock:
                failure_times.append(now)
                while (
                    failure_times
                    and (now - failure_times[0]).total_seconds() > failure_window_secs
                ):
                    failure_times.popleft()
                if len(failure_times) >= failure_threshold and not backoff_in_progress:
                    backoff_in_progress = True
                    need_backoff = True
                    backoff_event.clear()

            if need_backoff:
                self._log(
                    f"Task {task_id} consecutive failures reached {len(failure_times)}; backing off {backoff_sleep_secs}s",
                    level="warning",
                )
                await asyncio.sleep(backoff_sleep_secs)
                async with failure_lock:
                    failure_times.clear()
                    backoff_in_progress = False
                    backoff_event.set()

        async def _run_single(task_id: str, index: int) -> None:
            nonlocal tasks_running_result
            await asyncio.sleep(index * request_gap)  # Stagger start times

            try:
                task = self._load_task_from_disk(task_id)
            except Exception as exc:
                tasks_running_result.num_tasks_failed += 1
                self._log(f"Load task {task_id} failed: {exc}", level="error")
                progress.update(1)
                return

            if task.status != TaskStatus.PENDING:
                tasks_running_result.num_tasks_skipped += 1
                self._log(
                    f"Task {task.task_id} status {task.status.name}; skipping.",
                    level="info",
                )
                progress.update(1)
                return

            tasks_running_result.num_tasks_started += 1

            await backoff_event.wait()
            async with semaphore:
                await _update_inflight(1)
                task_result = await self.run_task(task)
                await _update_inflight(-1)

            if task_result.status == TaskStatus.COMPLETED:
                tasks_running_result.num_tasks_completed += 1
            elif task_result.status == TaskStatus.FAILED:
                tasks_running_result.num_tasks_failed += 1
                await _handle_failure_backoff(task_result.task_id)

            progress.update(1)

        await asyncio.gather(
            *(
                _run_single(task_id, idx)
                for idx, task_id in enumerate(self.config.task_ids)
            )
        )

        tasks_running_result.ended_at = datetime.now()
        progress.close()
        return tasks_running_result

    def _save_agent_config_to_disk(self) -> None:
        # Create the agents directory if it doesn't exist
        (self.data_dir / "agents").mkdir(parents=True, exist_ok=True)
        # Save the agent config to disk
        with open(self.data_dir / "agents" / f"{self.config.agent_id}.json", "w") as f:
            f.write(self.config.model_dump_json(indent=4))

    def _load_agent_config_from_disk(self, agent_id: str) -> AgentConfig:
        assert (self.data_dir / "agents" / f"{agent_id}.json").exists(), (
            f"Agent config not found for agent ID: {agent_id}"
        )
        # Load the agent config from disk
        with open(self.data_dir / "agents" / f"{agent_id}.json", "r") as f:
            # model_validate_json expects a JSON string, not a Python dict
            return AgentConfig.model_validate_json(f.read())

    def _save_task_to_disk(self, task: TaskSchema) -> None:
        # Create the tasks directory if it doesn't exist
        (self.data_dir / "tasks").mkdir(parents=True, exist_ok=True)
        # Save the task to disk
        with open(self.data_dir / "tasks" / f"{task.task_id}.json", "w") as f:
            f.write(task.model_dump_json(indent=4))

    def _load_task_from_disk(self, task_id: str) -> TaskSchema:
        assert (self.data_dir / "tasks" / f"{task_id}.json").exists(), (
            f"Task not found for task ID: {task_id}"
        )
        # Load the task from disk
        with open(self.data_dir / "tasks" / f"{task_id}.json", "r") as f:
            # model_validate_json expects a JSON string, not a Python dict
            return TaskSchema.model_validate_json(f.read())

    def _log(
        self, message: str, level: Literal["info", "warning", "error"] = "info"
    ) -> None:
        # Persist agent-scoped logs to disk instead of printing to stdout
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        with open(
            self.logs_dir / f"{self.config.agent_id}.log", "a", encoding="utf-8"
        ) as f:
            f.write(f"[{timestamp}] [{level.upper()}] {message}\n")

    def _get_successful_tasks(self) -> list[TaskSchema]:
        return [
            self._load_task_from_disk(task_id)
            for task_id in self.config.task_ids
            if self._load_task_from_disk(task_id).status == TaskStatus.COMPLETED
        ]
