from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError

with workflow.unsafe.imports_passed_through():
    from app.workflows.activities import run_scenario_activity


@dataclass
class RunInput:
    ids: list[str]
    commit: bool = False


@workflow.defn
class SqlScenarioWorkflow:
    @workflow.run
    async def run(self, inp: RunInput) -> list[dict]:
        results: list[dict] = []
        for sid in inp.ids:
            try:
                results.append(
                    await workflow.execute_activity(
                        run_scenario_activity, args=[sid, inp.commit],
                        start_to_close_timeout=timedelta(seconds=60),
                        retry_policy=RetryPolicy(maximum_attempts=3, non_retryable_error_types=["SqlStepError"]),
                    )
                )
            except ActivityError as exc:  # keep going; failure stays visible in the workflow history
                cause = exc.cause
                msg = cause.message if isinstance(cause, ApplicationError) else str(exc)
                results.append({"scenario_id": sid, "status": "failed", "duration_ms": 0, "steps": [], "error": msg})
        return results
