from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Assignment, Department, Employee, Project
from app.repository.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    def __init__(self, db: Session):
        super().__init__(db, Department)

    def payroll(self):
        stmt = (
            select(Department.name, func.count(Employee.id), func.coalesce(func.sum(Employee.salary), Decimal(0)))
            .outerjoin(Employee, Employee.department_id == Department.id)
            .group_by(Department.name)
            .order_by(Department.name)
        )
        return self.db.execute(stmt).all()


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: Session):
        super().__init__(db, Employee)

    def search(self, q=None, department_id=None, min_salary=None, skip=0, limit=50):
        stmt = select(Employee)
        if q:
            stmt = stmt.where(Employee.name.ilike(f"%{q}%"))
        if department_id:
            stmt = stmt.where(Employee.department_id == department_id)
        if min_salary:
            stmt = stmt.where(Employee.salary >= min_salary)
        return list(self.db.scalars(stmt.order_by(Employee.id).offset(skip).limit(limit)))


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)


class AssignmentRepository(BaseRepository[Assignment]):
    def __init__(self, db: Session):
        super().__init__(db, Assignment)

    def get_pair(self, employee_id: int, project_id: int):
        return self.db.get(Assignment, (employee_id, project_id))
