# Generated by Django 4.1.4 on 2022-12-13 12:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='course_edition_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]