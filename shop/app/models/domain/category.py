from dataclasses import dataclass

from shop.app.models.schemas import CategoryCreate


@dataclass
class CategoryCreateData:
    name: str

    @classmethod
    def from_input(cls, data: CategoryCreate) -> "CategoryCreateData":
        return cls(name=data.name)


@dataclass
class CategoryUpdateData:
    name: str | None = None


@dataclass
class Category:
    id: int
    name: str
