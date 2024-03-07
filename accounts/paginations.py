from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from mysite.settings import DEFAULT_PAGE_SIZE

class CustomPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
