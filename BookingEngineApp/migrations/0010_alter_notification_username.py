# Generated by Django 4.2.7 on 2024-04-11 11:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BookingEngineApp', '0009_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='username',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
