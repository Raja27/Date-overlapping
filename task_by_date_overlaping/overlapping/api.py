__author__ = 'rajaprasanna'

import datetime
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.response import Response
from .models import BaseTable
import overlapping.serializers as serializers


def str_to_date(date_str):
    try:
        if not isinstance(date_str, datetime.date):
            date_str = datetime.datetime.strptime(date_str, "%b %d %Y").date()
    except Exception as e:
        print(e)
    return date_str


def is_valid_dates(from_date, to_date):
    today = datetime.datetime.today().date()
    if not isinstance(from_date, datetime.date):
        from_date = str_to_date(from_date)
    if not isinstance(to_date, datetime.date):
        to_date = str_to_date(to_date)
    valid_dates = True if from_date >= today <= to_date else False
    return valid_dates


def create_reference(name, start_date, end_date, task):

    print('create_reference')
    if is_valid_dates(start_date, end_date):
        if not BaseTable.objects.filter(
                name=name, start_date__lte=end_date, end_date__gte=start_date).exists():
            reference = BaseTable(
                name=name, start_date=start_date, end_date=end_date, task=task).save()
            return reference, True
    return None, False


def clean_overlap(base_table, name, start_date, end_date):
    try:
        print('Cleaning template')
        if base_table.filter(start_date__gte=start_date, end_date__lte=end_date).exists():
            base_table.filter(start_date__gte=start_date, end_date__lte=end_date).delete()
            print('Delete and create')
            return True

        if base_table.filter(start_date__gte=start_date, start_date__lte=end_date,
                             end_date__gte=end_date).exists():
            new_date = str_to_date(end_date) + datetime.timedelta(days=1)
            base_table.filter(start_date__gte=start_date, start_date__lte=end_date,
                              end_date__gte=end_date).update(start_date=new_date)
            print('Re-assign start')
            return True
        if base_table.filter(end_date__gte=start_date, end_date__lte=end_date,
                             start_date__lte=start_date).exists():
            new_date = str_to_date(start_date) - datetime.timedelta(days=1)
            base_table.filter(
                end_date__gte=start_date, end_date__lte=end_date, start_date__lte=start_date
            ).update(end_date=new_date)
            print('Re-assign end')
            return True
        if base_table.filter(start_date__lte=start_date, end_date__gte=end_date).exists():
            new_end_date = str_to_date(start_date) - datetime.timedelta(days=1)
            new_start_date = str_to_date(end_date) + datetime.timedelta(days=1)
            new_references = base_table.filter(
                start_date__lte=start_date, end_date__gte=end_date)
            for new_reference in new_references:
                BaseTable(name=new_reference.name, start_date=new_start_date,
                          end_date=new_reference.end_date,
                          task=new_reference.task).save()
                new_reference.end_date = new_end_date
                new_reference.save()
            else:
                print('Inside')
                return True
    except Exception as e:
        print('Cleaning error', e)
        return False


def base_table_reference(base_table, name, start_date, end_date, task):

    if base_table.filter(
            Q(start_date__gte=start_date, start_date__lte=end_date)
            | Q(end_date__gte=start_date, end_date__lte=end_date)
    ).exists():
        if clean_overlap(base_table, name, start_date, end_date):
            print('Inner call')
            is_valid = base_table_reference(base_table, name, start_date, end_date, task)
    elif base_table.filter(start_date__lte=start_date, end_date__gte=end_date).exists():
        if clean_overlap(base_table, name, start_date, end_date):
            print('Inside call')
            is_valid = base_table_reference(base_table, name, start_date, end_date, task)
    else:
        new_reference, is_valid = create_reference(name, start_date, end_date, task)
    return is_valid


class BaseTableAPIView(APIView):

    def post(self, request, *args, **kwargs):
        print(datetime.datetime.now())
        response = {}
        status_message = 'Failed'
        status_code = status.HTTP_400_BAD_REQUEST
        data = request.data.copy()
        try:
            start_date = str_to_date(data.pop('start_date'))
            end_date = str_to_date(data.pop('end_date'))
            name = data.get('name')
            task = data.get('task')
            base_table = BaseTable.objects.filter(name=name)
            if base_table:
                is_valid = base_table_reference(base_table, name, start_date, end_date, task)
            else:
                new_reference, is_valid = create_reference(name, start_date, end_date, task)
            if is_valid:
                    status_code = status.HTTP_201_CREATED
                    status_message = 'Success'
            else:
                status_message = 'Date range claus with other dates'
        except Exception as e:
            print(e)
        response.update({'status_message': status_message})
        print(datetime.datetime.now())
        return Response(response, status_code)


class BaseTableListAPIView(ListAPIView):

    paginator_class = serializers.LimitTenPaginator
    serializer_class = serializers.BaseTableSerializer

    def get_queryset(self):
        return BaseTable.objects.all()