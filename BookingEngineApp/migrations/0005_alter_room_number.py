# Generated by Django 4.2.7 on 2024-04-07 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BookingEngineApp', '0004_alter_room_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='number',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
