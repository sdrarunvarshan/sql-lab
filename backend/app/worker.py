import asyncio
import logging

from temporalio.client import Client
from temporalio.contrib.opentelemetry import TracingInterceptor
from temporalio.worker import Worker

from app.core.config import settings
from app.core.database import init_db
from app.core.telemetry import setup_telemetry
from app.workflows.activities import run_scenario_activity
from app.workflows.sql_workflow import SqlScenarioWorkflow


async def main() -> None:
    init_db()
    setup_telemetry("sql-lab-worker")
    log = logging.getLogger("worker")
    while True:  # wait for Temporal server
        try:
            client = await Client.connect(settings.temporal_host, interceptors=[TracingInterceptor()])
            break
        except Exception as exc:  # noqa: BLE001
            log.warning("temporal not ready: %s", exc)
            await asyncio.sleep(3)
    log.info("worker listening on %s", settings.temporal_task_queue)
    await Worker(client, task_queue=settings.temporal_task_queue,
                 workflows=[SqlScenarioWorkflow], activities=[run_scenario_activity]).run()


if __name__ == "__main__":
    asyncio.run(main())
