from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: type[T]):
        self.db, self.model = db, model

    def get(self, id_: int) -> T | None:
        return self.db.get(self.model, id_)

    def list(self, skip: int = 0, limit: int = 50) -> list[T]:
        return list(self.db.scalars(select(self.model).offset(skip).limit(limit)))

    def add(self, **data) -> T:
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: T, **data) -> T:
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        self.db.delete(obj)
        self.db.commit()
