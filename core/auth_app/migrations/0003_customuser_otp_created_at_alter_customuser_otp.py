# Generated by Django 5.1.5 on 2025-02-22 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0002_customuser_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='otp_created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='otp',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
