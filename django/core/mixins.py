import logging
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone

from . import (
    chain,
    notifier,
)


log = logging.getLogger("core")


class BaseModelMixin:
    def is_new_record(self):
        return self._state.adding


class AddressMixin(BaseModelMixin):
    def reserve(self, timedelta_: timedelta):
        self.status = "BUSY"
        self.reserved_until = timezone.now() + timedelta_
        self.save()

    def free(self):
        self.status = "FREE"
        self.reserved_until = None
        self.save()

    def delete(self, *args, **kwargs):
        if self.qr_image:
            if os.path.isfile(self.qr_image.path):
                os.remove(self.qr_image.path)
        super().delete(*args, **kwargs)


class MerchantMixin(BaseModelMixin):
    def create_payment_methods(self):
        from .payment_methods import create_payment_methods
        create_payment_methods(self)

    def is_payment_method_available(
        self,
        coin_name: str,
        chain_name: str,
    ):
        return self.payment_methods.filter(
            coin_name=coin_name,
            chain_name__iexact=chain_name,
            is_enabled=True
        ).exists()

    def get_payment_method(
        self,
        coin_name: str,
        chain_name: str,
        is_enabled: bool = True
    ):
        return self.payment_methods.get(
            coin_name=coin_name,
            chain_name__iexact=chain_name,
            is_enabled=is_enabled,
        )


class InvoiceQuerySet(models.QuerySet):
    def not_confirming_now(self):
        return self.exclude(
            status__in=[
                "UNDERPAID",
                "PAID",
                "OVERPAID"
            ]
        )

    def whole_amount_confirmed(self):
        return self.filter(
            status__in=[
                "CONFIRMED",
                "OVERPAID_CONFIRMED"
            ],
        )

    def expired(self):
        return self.filter(
            expired_at__lte=timezone.now()
        )


class InvoiceProcessingManager(models.Manager):
    def get_queryset(self):
        return InvoiceQuerySet(self.model, using=self._db).filter(
            is_processing=True
        )

    def not_confirming_now(self):
        return self.get_queryset().not_confirming_now()

    def whole_amount_confirmed(self):
        return self.get_queryset().whole_amount_confirmed()

    def expired(self):
        return self.get_queryset().expired()


class InvoiceMixin(BaseModelMixin):

    def cancel(self):
        self.address.free()
        self.status = "CANCELED"
        self.is_processing = False
        self.save()

    def stop_processing(self):
        match self.status:
            case "UNPAID":
                self.status = "EXPIRED"
                self.is_successful = False
            case "UNDERPAID_CONFIRMED":
                self.is_successful = False
            case "CONFIRMED" | "OVERPAID_CONFIRMED":
                self.is_successful = True
            case "UNDERPAID" | "PAID" | "OVERPAID":
                raise Exception(
                    "Cannot stop processing UNDERPAID/PAID/OVERPAID "
                    "invoices because confirmations may spend long time"
                )

        self.address.free()
        self.is_processing = False
        self.save()

    def send_notification(self):
        if self.is_processing or self.is_successful is None:
            raise Exception(
                f"Invoice.id:{self.id} still processing. "
                "Please call Invoice.stop_processing() before"
            )
        response_json = notifier.CallbackClient(
            invoice=self
        ).send()
        self.is_notified = True
        self.save()
        return response_json

    def sync_chain_tranzes(self):
        chain.sync_chain_tranzes_for_invoice(self)

    def check_confirmations(self):
        amount_sent = self.get_total_sent_amount()
        if amount_sent == Decimal("0"):
            log.debug("Customer still send nothing")
            return
        amount_confirmed = self.get_total_confirmed_amount()

        if amount_sent == amount_confirmed:
            if amount_confirmed == self.amount:
                self.status = "CONFIRMED"
            elif amount_confirmed > self.amount:
                self.status = "OVERPAID_CONFIRMED"
            elif amount_confirmed < self.amount:
                self.status = "UNDERPAID_CONFIRMED"
        else:
            if amount_sent < self.amount:
                self.status = "UNDERPAID"
            elif amount_sent == self.amount:
                self.status = "PAID"
            elif amount_sent > self.amount:
                self.status = "OVERPAID"

        self.amount_confirmed = amount_confirmed
        self.save()

    def get_total_sent_amount(self):
        return self.transactions.filter(
            # confirmations__lt=self.payment_method.confirmations_required
            # Just get all invoice tranzes instead
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal("0.00")

    def get_total_confirmed_amount(self):
        return self.transactions.filter(
            confirmations__gte=self.payment_method.confirmations_required
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal("0.00")

    def is_my_tranz(self, sent_at: "datetime"):
        # TODO add tranz status FAIL check also
        return sent_at > self.created_at \
            and sent_at <= self.expired_at

    def update_or_create_tranz(
        self,
        txid: str,
        amount: Decimal,
        sent_at: "datetime",
        confirmations: int,
    ):
        from .models import Transaction
        log.debug(
            f"{self.payment_method} "
            f"tranz {txid} amount {amount} "
            f"has {confirmations} confirmations"
        )
        Transaction.objects.update_or_create(  # tranz, is_created =
            invoice=self,
            txid=txid,
            defaults={
                "amount": amount,
                "sent_at": sent_at,
                "confirmations": confirmations,
            }
        )

    def get_amount_rounded(self):
        return round(
            self.amount,
            self.payment_method.amount_decimal_rounding
        )


class TransactionMixin(BaseModelMixin):
    def get_amount_rounded(self):
        return round(
            self.amount,
            self.invoice.payment_method.amount_decimal_rounding
        )
