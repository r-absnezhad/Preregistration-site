# Generated by Django 4.2 on 2024-12-12 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pre_registration", "0006_alter_coursehistory_course_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="have_prerequisite_course",
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveField(
            model_name="course",
            name="prerequisite_course",
        ),
        migrations.AddField(
            model_name="course",
            name="prerequisite_course",
            field=models.ManyToManyField(
                blank=True,
                null=True,
                related_name="dependent_courses",
                to="pre_registration.course",
            ),
        ),
    ]
