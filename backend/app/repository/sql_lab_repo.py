"""Runs a scenario's statements one by one in a single transaction on the `lab` sandbox schema."""
import time

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.telemetry import tracer


class SqlStepError(Exception):
    def __init__(self, step: int, sql: str, message: str):
        super().__init__(f"step {step} failed: {message}")
        self.step, self.sql, self.message = step, sql, message


class SqlLabRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def run_steps(self, steps: tuple[str, ...], commit: bool = False, row_limit: int = 50) -> list[dict]:
        results: list[dict] = []
        with self.engine.connect() as conn:
            conn.execute(text("SET LOCAL search_path TO lab, public"))
            cur = conn.connection.cursor()  # raw DBAPI cursor: no bind-param parsing, so %, :: and $$ are safe
            for i, sql in enumerate(steps, 1):
                with tracer.start_as_current_span("sql.step") as span:
                    span.set_attribute("db.statement", sql)
                    span.set_attribute("sqllab.step", i)
                    t0 = time.perf_counter()
                    try:
                        cur.execute(sql)
                    except Exception as exc:  # noqa: BLE001
                        span.record_exception(exc)
                        conn.rollback()
                        raise SqlStepError(i, sql, str(exc).strip().splitlines()[0]) from exc
                    cols = [d.name for d in cur.description] if cur.description else []
                    rows = [list(r) for r in cur.fetchmany(row_limit)] if cur.description else []
                    results.append(
                        {
                            "step": i,
                            "sql": sql,
                            "command": cur.statusmessage,
                            "rowcount": cur.rowcount,
                            "columns": cols,
                            "rows": rows,
                            "ms": round((time.perf_counter() - t0) * 1000, 2),
                        }
                    )
            conn.commit() if commit else conn.rollback()
        return results
