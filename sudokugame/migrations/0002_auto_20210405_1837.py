# Generated by Django 3.1.6 on 2021-04-05 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sudokugame', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='postedDate',
            field=models.DateField(blank=True, null=True),
        ),
    ]