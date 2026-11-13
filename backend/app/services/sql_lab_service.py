import asyncio
import json
import time
import uuid

from fastapi import HTTPException

from app.core.config import settings
from app.core.database import engine
from app.core.telemetry import scenario_counter, scenario_duration, tracer
from app.repository.sql_lab_repo import SqlLabRepository, SqlStepError
from app.schemas.sql_lab import RunRequest, RunResponse, RunSummary
from app.services.sql_catalog import BY_ID, CATALOG

_repo = SqlLabRepository(engine)
_client = None


def run_scenario(scenario_id: str, commit: bool = False) -> dict:
    """Execute one scenario. Raises SqlStepError on SQL failure (Temporal activity turns that into a failed activity)."""
    sc = BY_ID[scenario_id]
    attrs = {"category": sc.category, "level": sc.level}
    t0 = time.perf_counter()
    with tracer.start_as_current_span(f"scenario {sc.id}") as span:
        span.set_attribute("sqllab.scenario", sc.id)
        try:
            steps = _repo.run_steps(sc.steps, commit=commit)
        except SqlStepError:
            scenario_counter.add(1, {**attrs, "status": "failed"})
            raise
        ms = round((time.perf_counter() - t0) * 1000, 2)
        scenario_counter.add(1, {**attrs, "status": "ok"})
        scenario_duration.record(ms, attrs)
    result = {"scenario_id": sc.id, "status": "ok", "duration_ms": ms, "steps": steps, "error": None}
    return json.loads(json.dumps(result, default=str))  # Decimal/date -> JSON-safe


def failed_result(scenario_id: str, error: str) -> dict:
    return {"scenario_id": scenario_id, "status": "failed", "duration_ms": 0, "steps": [], "error": error}


def run_scenario_safe(scenario_id: str, commit: bool) -> dict:
    try:
        return run_scenario(scenario_id, commit)
    except SqlStepError as exc:
        return failed_result(scenario_id, str(exc))


async def _temporal():
    global _client
    if _client is None:
        from temporalio.client import Client
        from temporalio.contrib.opentelemetry import TracingInterceptor

        _client = await Client.connect(settings.temporal_host, interceptors=[TracingInterceptor()])
    return _client


class SqlLabService:
    def catalog(self):
        return CATALOG

    async def run(self, req: RunRequest, is_admin: bool) -> RunResponse:
        ids = req.scenario_ids or [s.id for s in CATALOG]
        unknown = [i for i in ids if i not in BY_ID]
        if unknown:
            raise HTTPException(404, f"Unknown scenario(s): {', '.join(unknown)}")
        if req.commit and not is_admin:
            raise HTTPException(403, "Only admins can commit scenario changes")

        workflow_id = None
        if req.mode == "direct":
            results = [await asyncio.to_thread(run_scenario_safe, i, req.commit) for i in ids]
        else:
            from app.workflows.sql_workflow import RunInput, SqlScenarioWorkflow

            workflow_id = f"sql-lab-{uuid.uuid4().hex[:12]}"
            try:
                client = await _temporal()
                results = await client.execute_workflow(
                    SqlScenarioWorkflow.run, RunInput(ids, req.commit),
                    id=workflow_id, task_queue=settings.temporal_task_queue,
                )
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(503, f"Temporal unavailable: {exc}")

        ok = sum(r["status"] == "ok" for r in results)
        return RunResponse(mode=req.mode, workflow_id=workflow_id,
                           summary=RunSummary(total=len(results), ok=ok, failed=len(results) - ok), results=results)
