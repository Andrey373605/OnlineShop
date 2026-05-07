from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.errors import EmptyBrandNameError, InvalidBrandDescriptionError


def _normalize_brand_name(name: str) -> str:
    if not isinstance(name, str):
        raise EmptyBrandNameError("Brand name must be a string")
    clean = name.strip()
    if not clean:
        raise EmptyBrandNameError("Brand name cannot be empty")
    return clean


class Brand:
    def __init__(
        self,
        id: UUID,
        name: str,
        description: str | None,
        logo_image_id: UUID | None = None,
    ):
        self._id = id
        self._name = _normalize_brand_name(name)
        if description is None:
            self._description = None
        elif isinstance(description, str):
            self._description = description.strip()
        else:
            raise InvalidBrandDescriptionError("Brand description must be a string or null")
        self._logo_image_id = logo_image_id

    @classmethod
    def create(
        cls,
        name: str,
        description: str | None,
        logo_image_id: UUID | None = None,
    ) -> "Brand":
        return cls(
            id=uuid7(),
            name=name,
            description=description,
            logo_image_id=logo_image_id,
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def logo_image_id(self) -> UUID | None:
        return self._logo_image_id

    def change_name(self, new_name: str) -> None:
        self._name = _normalize_brand_name(new_name)

    def change_description(self, new_description: str | None) -> None:
        if new_description is None:
            self._description = None
            return
        if not isinstance(new_description, str):
            raise InvalidBrandDescriptionError("Brand description must be a string or null")
        stripped = new_description.strip()
        self._description = stripped if stripped else None

    def change_image_id(self, new_id: UUID | None) -> None:
        self._logo_image_id = new_id

    def __repr__(self) -> str:
        return f"<Brand {self._name} ({self._id})>"
