from collections import OrderedDict

from django.db.models import QuerySet
from rest_framework.pagination import LimitOffsetPagination as _LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response
from typing import Any, Type, List, Dict

from rest_framework.serializers import Serializer
from rest_framework.views import APIView


def get_paginated_response(
    *,
    pagination_class: Type[_LimitOffsetPagination],
    serializer_class: Type[Serializer],
    queryset: QuerySet,
    request: Request,
    view: APIView,
) -> Response:
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return Response(data=serializer.data)


class LimitOffsetPagination(_LimitOffsetPagination):
    default_limit: int = 100  # Set to 100 instead of 10
    max_limit: int = 100  # Keep this consistent

    def get_paginated_data(self, data: List[Dict[str, Any]]) -> OrderedDict:
        return OrderedDict(
            [
                ("limit", self.limit),
                ("offset", self.offset),
                ("count", self.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data: List[Dict[str, Any]]) -> Response:
        return Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
