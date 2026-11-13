from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    location: Mapped[str | None] = mapped_column(String(100))
    employees: Mapped[list["Employee"]] = relationship(back_populates="department")


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (CheckConstraint("salary > 0", name="ck_employee_salary_positive"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    salary: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    hire_date: Mapped[date]
    is_active: Mapped[bool] = mapped_column(default=True)
    skills: Mapped[list] = mapped_column(JSONB, default=list)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), index=True)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id", ondelete="SET NULL"))
    department: Mapped[Department | None] = relationship(back_populates="employees")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    start_date: Mapped[date | None]
    end_date: Mapped[date | None]
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))


class Assignment(Base):
    __tablename__ = "assignments"
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    hours: Mapped[int] = mapped_column(default=0)
    role: Mapped[str | None] = mapped_column(String(50))
