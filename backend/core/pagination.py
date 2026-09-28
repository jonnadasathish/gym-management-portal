"""API pagination convention (DEC-015): PageNumberPagination, default page
size 25, client-overridable up to a max of 100."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPageNumberPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "data": data,
                "meta": {
                    "page": self.page.number,
                    "page_size": self.get_page_size(self.request),
                    "total": self.page.paginator.count,
                    "total_pages": self.page.paginator.num_pages,
                },
            }
        )
