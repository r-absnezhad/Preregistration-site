# Generated by Django 4.2 on 2024-12-12 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pre_registration", "0009_category_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="slug",
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
