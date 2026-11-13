import asyncio

from temporalio import activity
from temporalio.exceptions import ApplicationError

from app.repository.sql_lab_repo import SqlStepError
from app.services.sql_lab_service import run_scenario


@activity.defn
async def run_scenario_activity(scenario_id: str, commit: bool) -> dict:
    activity.logger.info("running scenario %s (commit=%s)", scenario_id, commit)
    try:
        return await asyncio.to_thread(run_scenario, scenario_id, commit)
    except SqlStepError as exc:
        # SQL errors are deterministic -> do not retry; they appear as FAILED activities in Temporal UI
        raise ApplicationError(str(exc), exc.sql, type="SqlStepError", non_retryable=True) from exc
