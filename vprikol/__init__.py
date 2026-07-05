from .main import VprikolAPI
from .api import (VprikolAPIError, VprikolBadRequestError, VprikolAuthError, VprikolForbiddenError,
                  VprikolNotFoundError, VprikolConflictError, VprikolGoneError, VprikolRateLimitError,
                  VprikolValidationError, VprikolServerError)
from .backend import VprikolBackend
from .models import RatingType, EstateType, SSFont


def __getattr__(name: str):
    if name == "VprikolGrpcAPI":
        from .grpc_api import VprikolGrpcAPI
        return VprikolGrpcAPI
    raise AttributeError(f"module 'vprikol' has no attribute {name!r}")


__all__ = ["VprikolAPI", "VprikolAPIError", "VprikolBadRequestError", "VprikolAuthError", "VprikolForbiddenError",
           "VprikolNotFoundError", "VprikolConflictError", "VprikolGoneError", "VprikolRateLimitError",
           "VprikolValidationError", "VprikolServerError", "VprikolBackend", "VprikolGrpcAPI", "RatingType", "EstateType", "SSFont"]
