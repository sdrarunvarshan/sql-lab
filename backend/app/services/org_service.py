from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.repository.base import BaseRepository


class CrudService:
    """Generic CRUD with 404 / 409 translation. Business rules would be added in subclasses."""

    def __init__(self, repo: BaseRepository, label: str):
        self.repo, self.label = repo, label

    def get(self, id_: int):
        obj = self.repo.get(id_)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{self.label} {id_} not found")
        return obj

    def _guard(self, fn, *a, **kw):
        try:
            return fn(*a, **kw)
        except IntegrityError as exc:
            self.repo.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, f"{self.label}: {str(exc.orig).splitlines()[0]}")

    def create(self, data: dict):
        return self._guard(self.repo.add, **data)

    def update(self, id_: int, data: dict):
        return self._guard(self.repo.update, self.get(id_), **data)

    def delete(self, id_: int):
        self._guard(self.repo.delete, self.get(id_))
