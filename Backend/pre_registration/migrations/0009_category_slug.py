# Generated by Django 4.2 on 2024-12-12 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pre_registration", "0008_alter_course_prerequisite_course"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="slug",
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
