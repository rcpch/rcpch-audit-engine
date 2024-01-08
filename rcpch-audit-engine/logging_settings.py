"""These relate to logging settings."""

# Python imports
import os

CONSOLE_LOG_LEVEL = os.getenv("CONSOLE_LOG_LEVEL", "DEBUG")  # For e12 specific logs
CONSOLE_DJANGO_LOG_LEVEL = os.getenv(
    "CONSOLE_DJANGO_LOG_LEVEL", "DEBUG"
)  # For django logs
FILE_LOG_LEVEL = os.getenv("FILE_LOG_LEVEL", "DEBUG")

# Define the default django logger settings
django_loggers = {
    logger_name: {
        "handlers": ["django_console", "epilepsy12_logfile"],
        "level": CONSOLE_DJANGO_LOG_LEVEL,
        "propagate": False,
        "formatter": "simple_django",
    }
    for logger_name in (
        "django.request",
        "django.utils",  # The django.utils logger logs events from Django and other miscellaneous log events e.g. autoreload
        "django.security",
        "django.db.backends",  # The django.db.backends logger logs SQL queries. Set the level to DEBUG or higher to log SQL queries.
        "django.template",
        "django.server",  # The django.server logger logs events from the runserver command.
    )
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {},
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
        # Same as verbose, but no color formatting
        "file": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "verbose": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(bold_white)s%(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
            "log_colors": {
                "DEBUG": "bold_black",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        "simple": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s [%(name)s:%(lineno)s] %(bold_white)s%(message)s",
            "log_colors": {
                "DEBUG": "bold_black",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        # Don't need line numbers for default django loggers
        "simple_django": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s [%(name)s] %(bold_white)s%(message)s",
            "log_colors": {
                "DEBUG": "bold_black",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
    },
    "handlers": {
        "epilepsy12_console": {
            "level": CONSOLE_LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": [],
        },
        "django_console": {
            "level": CONSOLE_DJANGO_LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "simple_django",
            "filters": [],
        },
        # e12 file logger, each file is 15MB max, with 10 historic versions when filled, post-fixed with .1, .2, ..., .10
        "epilepsy12_logfile": {
            "level": FILE_LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/epilepsy12.log",
            "maxBytes": 15728640,  # 1024 * 1024 * 15B = 15MB
            "backupCount": 10,
            "formatter": "file",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["django_console", "epilepsy12_logfile"],
            "propagate": True,
        },
        **django_loggers,  # this injects the default django logger settings defined above
        "epilepsy12": {
            "handlers": ["epilepsy12_console", "epilepsy12_logfile"],
            "propagate": True,
        },
        "two_factor": {
            "handlers": ["epilepsy12_console", "epilepsy12_logfile"],
        },
    },
}
