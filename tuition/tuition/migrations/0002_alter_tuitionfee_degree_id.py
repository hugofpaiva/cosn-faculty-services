# Generated by Django 4.1.4 on 2022-12-14 22:51

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tuition', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tuitionfee',
            name='degree_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]