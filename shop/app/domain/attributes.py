from copy import deepcopy
from typing import Any

from shop.app.domain.errors import DomainValidationError


def coerce_attributes_dict(raw: dict[str, Any] | None) -> dict[str, Any]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise DomainValidationError("Attributes must be a dict")
    for key in raw:
        if not isinstance(key, str):
            raise DomainValidationError("Attribute keys must be strings")
    return deepcopy(raw)
