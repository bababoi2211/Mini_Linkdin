

from rest_framework.pagination import CursorPagination


class MyCursorPaginatior(CursorPagination):
    page_size = 10

    ordering = "is_admin"
