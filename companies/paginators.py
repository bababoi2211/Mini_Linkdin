

from rest_framework.pagination import CursorPagination


class CompanyPaginator(CursorPagination):
    page_size = 10
    ordering = "-rating"

