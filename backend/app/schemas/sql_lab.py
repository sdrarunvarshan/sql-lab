from typing import Any, Literal

from pydantic import BaseModel


class ScenarioOut(BaseModel):
    id: str
    category: str
    level: str
    title: str
    steps: list[str]


class RunRequest(BaseModel):
    scenario_ids: list[str] | None = None  # None => every scenario
    mode: Literal["temporal", "direct"] = "temporal"
    commit: bool = False  # admin only; default is run-and-rollback


class StepResult(BaseModel):
    step: int
    sql: str
    command: str | None
    rowcount: int
    columns: list[str]
    rows: list[list[Any]]
    ms: float


class ScenarioResult(BaseModel):
    scenario_id: str
    status: Literal["ok", "failed"]
    duration_ms: float
    steps: list[StepResult]
    error: str | None = None


class RunSummary(BaseModel):
    total: int
    ok: int
    failed: int


class RunResponse(BaseModel):
    mode: str
    workflow_id: str | None
    summary: RunSummary
    results: list[ScenarioResult]
