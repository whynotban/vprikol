from .main import VprikolAPI
from .api import (VprikolAPIError, VprikolBadRequestError, VprikolAuthError, VprikolForbiddenError,
                  VprikolNotFoundError, VprikolConflictError, VprikolGoneError, VprikolRateLimitError,
                  VprikolValidationError, VprikolServerError)
from .backend import VprikolBackend
from .models import (AnalyticsEventEntry, RatingType, EstateType, SSFont, SSTextAlign, SSOutputFormat, SSSettings, SSValidateResponse,
                     SSLineReport, SSLineIssue, SSIssueLevel, FONT_LABELS, FONTS_ORDER, DEFAULT_COMMAND_COLORS, COMMAND_LABELS)


def __getattr__(name: str):
    if name == "VprikolGrpcAPI":
        from .grpc_api import VprikolGrpcAPI
        return VprikolGrpcAPI
    raise AttributeError(f"module 'vprikol' has no attribute {name!r}")


__all__ = ["VprikolAPI", "VprikolAPIError", "VprikolBadRequestError", "VprikolAuthError", "VprikolForbiddenError",
           "VprikolNotFoundError", "VprikolConflictError", "VprikolGoneError", "VprikolRateLimitError",
           "VprikolValidationError", "VprikolServerError", "VprikolBackend", "VprikolGrpcAPI", "RatingType", "EstateType", "SSFont", "SSTextAlign", "SSOutputFormat",
           "SSSettings", "SSValidateResponse", "SSLineReport", "SSLineIssue", "SSIssueLevel", "FONT_LABELS", "FONTS_ORDER",
           "DEFAULT_COMMAND_COLORS", "COMMAND_LABELS", "AnalyticsEventEntry"]
