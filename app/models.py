from __future__ import print_function

import traceback

from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models


class CustomJSONField(JSONField):

    def contribute_to_class(self, cls, name):
        # print('\n\n', type(name), name)
        # traceback.print_stack()

        cls._meta.indexes.append(GinIndex(fields=[name]))
        # cls._meta.indexes.append(GinIndex(fields=[name]), name='manual_name_{}_gin'.format(cls._meta.db_table)))

        super(CustomJSONField, self).contribute_to_class(cls, name)


class Blog(models.Model):
    title = models.CharField(max_length=100)

    json = CustomJSONField()

    class Meta:
        indexes = []


# class Other(models.Model):
#     title = models.CharField(max_length=100)
#
#     json = CustomJSONField(default=dict)
