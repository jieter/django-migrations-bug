# Adding indexes in `Field.contribute_to_class()`

For [django-modeltrans](https://github.com/zostera/django-modeltrans) I use a field derived from `django.contrib.postgres.fields.JSONField` for which I want to add a `GinIndex`.

My [naive implementation](https://github.com/zostera/django-modeltrans/blob/37db54b9ddbd6bf2c58874bba800d4c425cb8a5a/modeltrans/fields.py#L252-L253) works when the field is added along with a new model.

When I strip down that field, this is what's left:

```python
class CustomJSONField(JSONField):
    def contribute_to_class(self, cls, name):
        super(CustomJSONField, self).contribute_to_class(cls, name)

        index = GinIndex(fields=[name])
        index.set_name_with_model(cls)
        cls._meta.indexes.append(index)
```

When add a new model:

```python
class Blog(models.Model):
    title = models.CharField(max_length=100)

    json = CustomJSONField()
```

```
./manage.py --version
1.11.8
./manage.py makemigrations app
Migrations for 'app':
  app/migrations/0001_initial.py
    - Create model Blog
    - Create index app_blog_json_2cf556_gin on field(s) json of model blog
```

This is like expected, `operations` list from `migrations/0001_initial.py`:

```python
operations = [
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
        index=django.contrib.postgres.indexes.GinIndex(fields=['json'], name='app_blog_json_2cf556_gin'),
    ),
]
```

Then, when I add `class Meta: indexes = []`:

```python
class Blog(models.Model):
    title = models.CharField(max_length=100)

    json = CustomJSONField()

    class Meta:
        indexes = []
```

```
rm -rf app/migrations
pip install django==1.11.8
./manage.py --version
1.11.8
./manage.py makemigrations app
Migrations for 'app':
  app/migrations/0001_initial.py
    - Create model Blog
    - Create index app_blog_json_2cf556_gin on field(s) json of model blog
    - Create index app_blog_json_2cf556_gin on field(s) json of model blog
```

The index is added twice (with the same name, resulting in `django.db.utils.ProgrammingError: relation "app_blog_json_2cf556_gin" already exists`).

If I add `class Meta: indexes = []` after the initial migration in done, no changes are detected.


## When names are created

The django generated index name is set when [`index.set_name_with_model(model)` is called in `ModelState`](https://github.com/django/django/blob/1.11/django/db/migrations/state.py#L466).

Omitting the `name` argument is not possible, because apparently, `index.set_name_with_model()` is not called on the elements added to `Model._meta.indexes` from `contribute_to_class`.
That's why I do it manually from `contribute_to_class`


# related issues/comments
 - https://code.djangoproject.com/ticket/27738
[Markus Holtermann](https://code.djangoproject.com/ticket/27738#comment:4)
> name is supposed to be a required argument when you define an index in `_meta.indexes`. However, for backwards compatibility reasons with auto-generated index names for e.g. db_index=True and index_together the name cannot be set during object creation but needs to be patched in later while running migrations.
 - Django ticket created as a result of this tinkering: [Index added to _meta.indexes with Meta.indexes=[] yields two equal addIndex() operations.](https://code.djangoproject.com/ticket/28888)
