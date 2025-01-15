# Generated by Django 5.1.4 on 2025-01-08 04:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formhandling', '0005_apilog'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('failed_attempts', models.IntegerField(default=0)),
                ('lockout_time', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='login_attempt', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
