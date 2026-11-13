from fastapi import APIRouter, Depends

from app.router.deps import current_user
from app.schemas.sql_lab import RunRequest, RunResponse, ScenarioOut
from app.services.sql_lab_service import SqlLabService

router = APIRouter(prefix="/sql-lab", tags=["sql-lab"])


@router.get("/scenarios", response_model=list[ScenarioOut])
def scenarios(_=Depends(current_user)):
    return [ScenarioOut(id=s.id, category=s.category, level=s.level, title=s.title, steps=list(s.steps))
            for s in SqlLabService().catalog()]


@router.post("/run", response_model=RunResponse)
async def run(body: RunRequest, user=Depends(current_user)):
    """Run one, several (scenario_ids) or all scenarios, via Temporal (default) or directly."""
    return await SqlLabService().run(body, is_admin=user.role == "admin")
