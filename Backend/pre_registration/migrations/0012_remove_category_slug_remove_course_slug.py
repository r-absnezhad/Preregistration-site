# Generated by Django 4.2 on 2024-12-15 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pre_registration", "0011_rename_course_id_registrations_courses_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="category",
            name="slug",
        ),
        migrations.RemoveField(
            model_name="course",
            name="slug",
        ),
    ]
