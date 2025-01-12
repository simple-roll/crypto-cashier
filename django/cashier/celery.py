import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cashier.settings")
app = Celery("cashier")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


def _get_interval(env_name, default):
    return int(os.getenv(env_name, default))


app.conf.beat_schedule = {
    'tranzes-chain-sync': {
        'task': (
            'core.tasks'
            '.sync_chain_tranzes_for_all_processing_invoices'
        ),
        'schedule': _get_interval("BEAT_SYNC_CHAIN_TRANZES_INTERVAL", 60),
    },
    'tranzes-confirmations-check': {
        'task': (
            'core.tasks'
            '.check_tranzes_confirmations_for_all_processing_invoices'
        ),
        'schedule': _get_interval("BEAT_TRANZES_CONFIRM_CHECK_INTERVAL", 30)
    },
    'handle-confirmed-invoices': {
        'task': (
            'core.tasks'
            '.handle_confirmed_invoices'
        ),
        'schedule': _get_interval("BEAT_HANDLE_CONFIRMED_INVOICES_INTERVAL", 30)
    },
    'handle-expired-invoices': {
        'task': (
            'core.tasks'
            '.handle_expired_invoices'
        ),
        'schedule': _get_interval("BEAT_HANDLE_EXPIRED_INVOICES_INTERVAL", 30)
    },
}
