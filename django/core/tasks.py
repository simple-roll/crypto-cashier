# from django.utils import timezone
from celery import shared_task
import logging
from . import models


log = logging.getLogger("core")


@shared_task
def sync_chain_tranzes_for_all_processing_invoices():
    invoices = models.Invoice.processing.all()

    if invoices.count() == 0:
        log.debug("No processing invoices")
        return

    for invoice in invoices:
        sync_chain_tranzes_for_invoice.delay(invoice.id)


@shared_task
def sync_chain_tranzes_for_invoice(invoice_id):
    invoice = models.Invoice.objects.get(pk=invoice_id)
    log.debug(f"Sync chain tranzes for {invoice}")
    invoice.sync_chain_tranzes()


@shared_task
def check_tranzes_confirmations_for_all_processing_invoices():
    invoices = models.Invoice.processing.filter(
        transactions__isnull=False,
    ).all()
    for invoice in invoices:
        check_chain_tranzes_for_invoice.delay(invoice.id)


@shared_task
def check_chain_tranzes_for_invoice(invoice_id):
    invoice = models.Invoice.objects.get(pk=invoice_id)
    log.debug(f"Check chain tranzes for {invoice}")
    invoice.check_confirmations()


@shared_task
def handle_confirmed_invoices():
    invoices = models.Invoice.processing.whole_amount_confirmed()
    for invoice in invoices:
        stop_processing_invoice.delay(invoice.id)


@shared_task
def handle_expired_invoices():
    invoices = models.Invoice.processing\
        .expired().not_confirming_now()

    for invoice in invoices:
        stop_processing_invoice.delay(invoice.id)


@shared_task
def stop_processing_invoice(invoice_id):
    invoice = models.Invoice.objects.get(pk=invoice_id)
    invoice.stop_processing()  # Must be first
    invoice.send_notification()
