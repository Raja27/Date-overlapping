# coding=utf-8

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class BaseTable(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    task = models.CharField(_('Task'), max_length=255, default='Init')

    def __str__(self):
        return "%s" % self.name

    class Meta():

        db_table = 'base_tables'
        verbose_name = _('Base Table')
        verbose_name_plural = _('Base Tables')
        ordering = ('name', 'start_date')