# Generated by Django 5.0.3 on 2024-05-17 09:11

import datetime
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epilepsy12", "0027_episode_focal_onset_laterality_unknown_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="epilepsy12user",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    2024, 5, 17, 9, 9, 38, 16872, tzinfo=datetime.timezone.utc
                ),
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="epilepsy12user",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_users",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="epilepsy12user",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="epilepsy12user",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="updated_users",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalepilepsy12user",
            name="created_at",
            field=models.DateTimeField(
                blank=True, default=django.utils.timezone.now, editable=False
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalepilepsy12user",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalepilepsy12user",
            name="updated_at",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2024, 5, 17, 9, 11, 8, 750171, tzinfo=datetime.timezone.utc
                ),
                editable=False,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalepilepsy12user",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="historicalinvestigations",
            name="mri_indicated",
            field=models.BooleanField(
                blank=True,
                default=None,
                help_text={
                    "label": "Has a brain MRI been achieved?",
                    "reference": "NICE recommends that an MRI scan should be offered to children, young people and adults diagnosed with epilepsy, unless they have idiopathic generalised epilepsy or self-limited epilepsy with centrotemporal spikes. The MRI should be carried out within 6 weeks of the MRI referral.",
                },
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="investigations",
            name="mri_indicated",
            field=models.BooleanField(
                blank=True,
                default=None,
                help_text={
                    "label": "Has a brain MRI been achieved?",
                    "reference": "NICE recommends that an MRI scan should be offered to children, young people and adults diagnosed with epilepsy, unless they have idiopathic generalised epilepsy or self-limited epilepsy with centrotemporal spikes. The MRI should be carried out within 6 weeks of the MRI referral.",
                },
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="visitactivity",
            name="activity",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "SUCCESSFUL_LOGIN"),
                    (2, "UNSUCCESSFUL_LOGIN"),
                    (3, "LOGOUT"),
                    (4, "PASSWORD_RESET_LINK_SENT"),
                    (5, "PASSWORD_RESET"),
                    (6, "SETUP_TWO_FACTOR_AUTHENTICATION"),
                ],
                default=1,
            ),
        ),
    ]
