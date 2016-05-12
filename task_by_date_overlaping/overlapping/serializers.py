__author__ = 'rajaprasanna'
from rest_framework import serializers, pagination
from .models import BaseTable


class LimitTenPaginator(pagination.PageNumberPagination):
    default_limit = 10
    page_size_query_param = 'limit'


class BaseTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseTable