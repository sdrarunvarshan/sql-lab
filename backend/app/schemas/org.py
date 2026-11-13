from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class _Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DepartmentIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    budget: Decimal = Decimal("0")
    location: str | None = None


class DepartmentPatch(BaseModel):
    name: str | None = None
    budget: Decimal | None = None
    location: str | None = None


class DepartmentOut(_Out, DepartmentIn):
    id: int


class DepartmentPayroll(BaseModel):
    department: str
    headcount: int
    payroll: Decimal


class EmployeeIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    salary: Decimal = Field(gt=0)
    hire_date: date
    is_active: bool = True
    skills: list[str] = []
    department_id: int | None = None
    manager_id: int | None = None


class EmployeePatch(BaseModel):
    name: str | None = None
    salary: Decimal | None = Field(default=None, gt=0)
    is_active: bool | None = None
    skills: list[str] | None = None
    department_id: int | None = None
    manager_id: int | None = None


class EmployeeOut(_Out, EmployeeIn):
    id: int


class ProjectIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    budget: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
    department_id: int | None = None


class ProjectOut(_Out, ProjectIn):
    id: int


class AssignmentIn(BaseModel):
    employee_id: int
    project_id: int
    hours: int = Field(default=0, ge=0)
    role: str | None = None


class AssignmentOut(_Out, AssignmentIn):
    pass
