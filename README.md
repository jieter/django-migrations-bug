# Adding indexes in `Field.contribute_to_class()`

For [django-modeltrans](https://github.com/zostera/django-modeltrans) I use a field derived from `django.contrib.postgres.fields.JSONField` for which I want to add a `GinIndex`.

My [naive implementation](https://github.com/zostera/django-modeltrans/blob/37db54b9ddbd6bf2c58874bba800d4c425cb8a5a/modeltrans/fields.py#L252-L253) works when the field is added along with a new model.

When I strip down that field, this is what's left:

```python
class CustomJSONField(JSONField):

    def contribute_to_class(self, cls, name):
        cls._meta.indexes.append(GinIndex(fields=[name], name='manual_name_{}_gin'.format(cls._meta.db_table)))

        super(CustomJSONField, self).contribute_to_class(cls, name)
```

When add a new model:

```python
class Blog(models.Model):
    title = models.CharField(max_length=100)

    json = CustomJSONField()
```

```
$ ./manage.py --version && ./manage.py makemigrations app
1.11.8
Migrations for 'app':
  app/migrations/0001_initial.py
    - Create model Blog
```

Note that the indexes are added in the migration, but not mentioned in the output. Relevant part of the migration (containing the index, but with the manual name):
```python
    migrations.CreateModel(
        name='Blog',
        fields=[
            ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('title', models.CharField(max_length=100)),
            ('json', app.models.CustomJSONField()),
        ],
    ),
    migrations.AddIndex(
        model_name='blog',
        index=django.contrib.postgres.indexes.GinIndex(fields=['json'], name=b'manual_name_app_blog_gin'),
    ),
```

Then, when I add `class Meta: indexes = []`:

```python
class Blog(models.Model):
    title = models.CharField(max_length=100)

    json = CustomJSONField()

    class Meta:
        indexes = []
```

For django 1.11:
```
$ ./manage.py --version && ./manage.py makemigrations app
1.11
Migrations for 'app':
  app/migrations/0001_initial.py
    - Create model Blog
    - Create index app_blog_json_2cf556_gin on field(s) json of model blog
    - Create index manual_name_app_blog_gin on field(s) json of model blog
```

For django 1.11.8:
```
$ ./manage.py --version && ./manage.py makemigrations app
1.11.8
Migrations for 'app':
  app/migrations/0001_initial.py
    - Create model Blog
    - Create index manual_name_app_blog_gin on field(s) json of model blog
    - Create index manual_name_app_blog_gin on field(s) json of model blog
```

the django generated index name is set when [`index.set_name_with_model(model)` is called in `ModelState`](https://github.com/django/django/blob/1.11/django/db/migrations/state.py#L466).

Django 1.11.1 added a backport from [PR #8328](https://github.com/django/django/pull/8328) which checks if index.name is defined, so we should expect this behaviour. Omitting the `name` argument is not possible, because apparently, `index.set_name_with_model()` is not called on the elements added to `Model._meta.indexes` from `contribute_to_class`.


When I omit the `name` argument from `GinIndex()`, I get:

```
$ ./manage.py --version && ./manage.py makemigrations app
1.11
[... stack trace ...]
ValueError: Indexes passed to AddIndex operations require a name argument. <GinIndex: fields='json'> doesn't have one.
```

Results for 1.11.8 and 2.0 are the same.

Ideally, I want to rely on Django to generate the name.
