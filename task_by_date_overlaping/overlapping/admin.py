from django.contrib import admin
from django.apps import apps

from .models import BaseTable


class DynamicColumnAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super(DynamicColumnAdmin, self).__init__(*args, **kwargs)
        fields_list = [i.name for i in self.model._meta.fields]
        self.list_display = fields_list
        self.list_display_links = fields_list

admin.site.register(BaseTable, DynamicColumnAdmin)