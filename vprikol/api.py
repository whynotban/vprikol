from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class VprikolAPIError(Exception):
    def __init__(self, status_code: int, error_data: Any):
        self.status_code = status_code
        self.error_data = dict(error_data) if isinstance(error_data, Mapping) else {"detail": error_data}
        self.detail = self.error_data.get("detail", self.error_data)
        super().__init__(f"API веселого прикола вернуло ошибку {self.status_code}: {self.detail}")


class VprikolBadRequestError(VprikolAPIError):
    pass


class VprikolAuthError(VprikolAPIError):
    pass


class VprikolForbiddenError(VprikolAPIError):
    pass


class VprikolNotFoundError(VprikolAPIError):
    pass


class VprikolConflictError(VprikolAPIError):
    pass


class VprikolGoneError(VprikolAPIError):
    pass


class VprikolRateLimitError(VprikolAPIError):
    pass


class VprikolValidationError(VprikolAPIError):
    pass


class VprikolServerError(VprikolAPIError):
    pass


ERROR_BY_STATUS = {
    400: VprikolBadRequestError,
    401: VprikolAuthError,
    403: VprikolForbiddenError,
    404: VprikolNotFoundError,
    409: VprikolConflictError,
    410: VprikolGoneError,
    422: VprikolValidationError,
    429: VprikolRateLimitError,
}


def create_api_error(status_code: int, error_data: Any) -> VprikolAPIError:
    error_cls = ERROR_BY_STATUS.get(status_code, VprikolServerError if status_code >= 500 else VprikolAPIError)
    return error_cls(status_code=status_code, error_data=error_data)
