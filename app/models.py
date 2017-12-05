from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models


class CustomJSONField(JSONField):
    def contribute_to_class(self, cls, name):
        super(CustomJSONField, self).contribute_to_class(cls, name)

        index = GinIndex(fields=[name])
        index.set_name_with_model(cls)
        cls._meta.indexes.append(index)


class Blog(models.Model):
    title = models.CharField(max_length=100)
    json = CustomJSONField(default=dict)

    class Meta:
        indexes = []

# class Other(models.Model):
#     title = models.CharField(max_length=100)
#     json = CustomJSONField(default=dict)
