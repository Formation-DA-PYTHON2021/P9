# Generated by Django 4.1 on 2022-09-15 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_review_ticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='review_associate',
            field=models.BooleanField(default=False),
        ),
    ]