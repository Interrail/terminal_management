from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler


def create_serializer_class(name, fields):
    return type(name, (serializers.Serializer,), fields)


def inline_serializer(*, fields, data=None, **kwargs):
    # Important note if you are using `drf-spectacular`
    # Please refer to the following issue:
    # https://github.com/HackSoftware/Django-Styleguide/issues/105#issuecomment-1669468898
    # Since you might need to use unique names (uuids) for each inline serializer
    serializer_class = create_serializer_class(name="inline_serializer", fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)


class ApplicationError(Exception):
    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}


def custom_exception_handler(exc, ctx):
    """
    {
        "message": "Error message",
        "extra": {}
    }
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, ctx)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        if isinstance(exc, ApplicationError):
            data = {"message": exc.message, "extra": exc.extra}
            return Response(data, status=400)

        return response

    if isinstance(exc.detail, (list, dict)):
        response.data = {"detail": response.data}

    if isinstance(exc, exceptions.ValidationError):
        response.data["message"] = "Validation error"
        response.data["extra"] = {"fields": response.data["detail"]}
    else:
        response.data["message"] = response.data["detail"]
        response.data["extra"] = {}

    del response.data["detail"]

    return response
