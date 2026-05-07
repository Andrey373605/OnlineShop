
from shop.app.domain.errors.base import DomainError


class EmptyBrandNameError(DomainError):
    pass


class InvalidBrandDescriptionError(DomainError):
    pass


class EmptyCategoryNameError(DomainError):
    pass


class EmptyRoleNameError(DomainError):
    pass


class EmptyPermissionNameError(DomainError):
    pass


class EmptyWarehouseNameError(DomainError):
    pass


class EmptyProductTitleError(DomainError):
    pass
