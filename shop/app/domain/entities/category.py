from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.errors import EmptyCategoryNameError

if TYPE_CHECKING:
    from shop.app.models.schemas.category_schemas import CategoryCreate, CategoryUpdate


def _normalize_category_name(name: str) -> str:
    if not isinstance(name, str):
        raise EmptyCategoryNameError("Category name must be a string")
    clean = name.strip()
    if not clean:
        raise EmptyCategoryNameError("Category name cannot be empty")
    return clean


class Category:
    def __init__(
        self,
        id: UUID,
        name: str,
    ):
        self._id = id
        self._name = _normalize_category_name(name)

    @classmethod
    def create(cls, name: str) -> "Category":
        return cls(id=uuid7(), name=name)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def change_name(self, new_name: str) -> None:
        normalized = _normalize_category_name(new_name)
        if self._name != normalized:
            self._name = normalized

    def __repr__(self) -> str:
        return f"<Category {self._name} ({self._id})>"


@dataclass(frozen=True)
class CategoryCreateData:
    """Input for persisting a new category (application → repository)."""

    name: str

    @classmethod
    def from_input(cls, data: CategoryCreate) -> CategoryCreateData:
        return cls(name=data.name)


@dataclass(frozen=True)
class CategoryUpdateData:
    """Partial fields for updating a category row."""

    name: str | None = None

    @classmethod
    def from_input(cls, data: CategoryUpdate) -> CategoryUpdateData:
        return cls(**data.model_dump(exclude_unset=True))
