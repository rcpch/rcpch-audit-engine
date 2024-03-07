# Python Imports
from typing import Literal, Union
from datetime import date
import logging

# Django Imports
from django.utils.html import strip_tags
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings

# Third party imports
from celery import shared_task

# E12 Imports
from .general_functions import cohort_number_from_first_paediatric_assessment_date
from epilepsy12.constants import EnumAbstractionLevel
from epilepsy12.common_view_functions.aggregate_by import update_all_kpi_agg_models
from epilepsy12.management.commands.old_pt_data_scripts import insert_old_pt_data
from epilepsy12.management.commands.user_scripts import insert_user_data

# Logging setup
logger = logging.getLogger(__name__)

@shared_task
def send_email_to_recipients(
    recipients: list, subject: str, message: str
):
    """
    Sends emails
    """
    try:
        send_mail(
            subject=subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
            message=strip_tags(message),
            html_message=message,
        )
    except Exception:
        raise BadHeaderError

@shared_task
def hello():
    """
    THIS IS A SCHEDULED TASK THAT IS CALLED AT 06:00 EVERY DAY
    THE CRON DATE/FREQUENCY IS SET IN SETTING.PY
    """
    logger.debug("0600 cron check task ran successfully")
