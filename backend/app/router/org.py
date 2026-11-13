from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.org_repo import AssignmentRepository, DepartmentRepository, EmployeeRepository, ProjectRepository
from app.router.deps import admin_only, current_user
from app.schemas.org import (AssignmentIn, AssignmentOut, DepartmentIn, DepartmentOut, DepartmentPatch,
                             DepartmentPayroll, EmployeeIn, EmployeeOut, EmployeePatch, ProjectIn, ProjectOut)
from app.services.org_service import CrudService

router = APIRouter(dependencies=[Depends(current_user)])


def _svc(repo_cls, label):
    return lambda db=Depends(get_db): CrudService(repo_cls(db), label)


dept_svc, emp_svc = _svc(DepartmentRepository, "Department"), _svc(EmployeeRepository, "Employee")
proj_svc, asg_svc = _svc(ProjectRepository, "Project"), _svc(AssignmentRepository, "Assignment")

# ---- departments
@router.get("/departments", response_model=list[DepartmentOut], tags=["departments"])
def list_departments(skip: int = 0, limit: int = Query(50, le=200), s: CrudService = Depends(dept_svc)):
    return s.repo.list(skip, limit)


@router.get("/departments/payroll", response_model=list[DepartmentPayroll], tags=["departments"])
def payroll(db: Session = Depends(get_db)):
    return [DepartmentPayroll(department=n, headcount=c, payroll=p) for n, c, p in DepartmentRepository(db).payroll()]


@router.post("/departments", response_model=DepartmentOut, status_code=201, tags=["departments"])
def create_department(body: DepartmentIn, s: CrudService = Depends(dept_svc)):
    return s.create(body.model_dump())


@router.get("/departments/{id}", response_model=DepartmentOut, tags=["departments"])
def get_department(id: int, s: CrudService = Depends(dept_svc)):
    return s.get(id)


@router.patch("/departments/{id}", response_model=DepartmentOut, tags=["departments"])
def patch_department(id: int, body: DepartmentPatch, s: CrudService = Depends(dept_svc)):
    return s.update(id, body.model_dump(exclude_unset=True))


@router.delete("/departments/{id}", status_code=204, dependencies=[Depends(admin_only)], tags=["departments"])
def delete_department(id: int, s: CrudService = Depends(dept_svc)):
    s.delete(id)

# ---- employees
@router.get("/employees", response_model=list[EmployeeOut], tags=["employees"])
def list_employees(q: str | None = None, department_id: int | None = None, min_salary: Decimal | None = None,
                   skip: int = 0, limit: int = Query(50, le=200), s: CrudService = Depends(emp_svc)):
    return s.repo.search(q, department_id, min_salary, skip, limit)


@router.post("/employees", response_model=EmployeeOut, status_code=201, tags=["employees"])
def create_employee(body: EmployeeIn, s: CrudService = Depends(emp_svc)):
    return s.create(body.model_dump())


@router.get("/employees/{id}", response_model=EmployeeOut, tags=["employees"])
def get_employee(id: int, s: CrudService = Depends(emp_svc)):
    return s.get(id)


@router.patch("/employees/{id}", response_model=EmployeeOut, tags=["employees"])
def patch_employee(id: int, body: EmployeePatch, s: CrudService = Depends(emp_svc)):
    return s.update(id, body.model_dump(exclude_unset=True))


@router.delete("/employees/{id}", status_code=204, dependencies=[Depends(admin_only)], tags=["employees"])
def delete_employee(id: int, s: CrudService = Depends(emp_svc)):
    s.delete(id)

# ---- projects & assignments
@router.get("/projects", response_model=list[ProjectOut], tags=["projects"])
def list_projects(skip: int = 0, limit: int = Query(50, le=200), s: CrudService = Depends(proj_svc)):
    return s.repo.list(skip, limit)


@router.post("/projects", response_model=ProjectOut, status_code=201, tags=["projects"])
def create_project(body: ProjectIn, s: CrudService = Depends(proj_svc)):
    return s.create(body.model_dump())


@router.get("/projects/{id}", response_model=ProjectOut, tags=["projects"])
def get_project(id: int, s: CrudService = Depends(proj_svc)):
    return s.get(id)


@router.delete("/projects/{id}", status_code=204, dependencies=[Depends(admin_only)], tags=["projects"])
def delete_project(id: int, s: CrudService = Depends(proj_svc)):
    s.delete(id)


@router.post("/assignments", response_model=AssignmentOut, status_code=201, tags=["projects"])
def assign(body: AssignmentIn, s: CrudService = Depends(asg_svc)):
    return s.create(body.model_dump())


@router.delete("/assignments/{employee_id}/{project_id}", status_code=204, tags=["projects"])
def unassign(employee_id: int, project_id: int, s: CrudService = Depends(asg_svc)):
    from fastapi import HTTPException
    obj = s.repo.get_pair(employee_id, project_id)
    if not obj:
        raise HTTPException(404, "Assignment not found")
    s.repo.delete(obj)
