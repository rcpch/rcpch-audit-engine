# Generated by Django 4.1.5 on 2023-01-22 15:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy12', '0047_alter_kpi_options_historicalsyndrome_historicalsite_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_datetime', models.DateTimeField(blank=True, null=True)),
                ('login_failed_datetime', models.DateTimeField(blank=True, null=True)),
                ('logout_datetime', models.DateTimeField(blank=True, null=True)),
                ('ip_address', models.CharField(blank=True, max_length=250, null=True)),
                ('epilepsy12user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
