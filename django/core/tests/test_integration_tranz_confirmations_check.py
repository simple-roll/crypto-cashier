from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from faker import Faker
from faker.providers import date_time

from core import models
import ethereum.scanapi
from . import (
    factories,
    utils,
)

faker = Faker()
faker.add_provider(date_time)


class TranzConfirmationsCheck(TestCase):
    @staticmethod
    def _create_case(
        invoice_amount: Decimal,
        tranzes_total_sent_amount: Decimal,
        tranzes_count: int,
        tranzes_confirmed_count: int,
    ):
        confirmations_required = 10
        invoice = factories.InvoiceFactory(
            amount=invoice_amount,
            status="UNPAID",
            payment_method=factories.PaymentMethodFactory(
                confirmations_required=confirmations_required
            )
        )
        for tranz in range(tranzes_count):
            if tranzes_confirmed_count > 0:
                # Confirmed tranz
                confirmations = faker.pyint(
                    confirmations_required, 1000  # min, max
                )
                tranzes_confirmed_count -= 1
            else:
                # Not confirmed tranz
                confirmations = faker.pyint(
                    0, confirmations_required - 1  # min, max
                )

            factories.TransactionFactory(
                invoice=invoice,
                amount=(
                    tranzes_total_sent_amount / tranzes_count
                ),
                confirmations=confirmations
            )

        return invoice

    def test_invoice_unpaid(self):
        invoice = self._create_case(
            invoice_amount=Decimal("100.00"),
            tranzes_total_sent_amount=Decimal("0.00"),
            tranzes_count=0,
            tranzes_confirmed_count=0,
        )
        invoice.check_confirmations()
        self.assertEqual(
            invoice.status, "UNPAID"
        )

    def test_invoice_paid(self):
        invoice = self._create_case(
            invoice_amount=Decimal("100.00"),
            tranzes_total_sent_amount=Decimal("100.00"),
            tranzes_count=4,
            tranzes_confirmed_count=2,
        )
        invoice.check_confirmations()
        self.assertEqual(
            invoice.status, "PAID"
        )

    def test_invoice_underpaid_case(self):
        invoice = self._create_case(
            invoice_amount=Decimal("100.00"),
            tranzes_total_sent_amount=Decimal("75.00"),
            tranzes_count=4,
            tranzes_confirmed_count=2,
        )
        invoice.check_confirmations()
        self.assertEqual(
            invoice.status, "UNDERPAID"
        )

    def test_invoice_overpaid_case(self):
        invoice = self._create_case(
            invoice_amount=Decimal("100.00"),
            tranzes_total_sent_amount=Decimal("125.00"),
            tranzes_count=4,
            tranzes_confirmed_count=2,
        )
        invoice.check_confirmations()
        self.assertEqual(
            invoice.status, "OVERPAID"
        )

    def test_invoice_confirmed_case(self):
        invoice = self._create_case(
            invoice_amount=Decimal("100.00"),
            tranzes_total_sent_amount=Decimal("100.00"),
            tranzes_count=4,
            tranzes_confirmed_count=4,
        )
        invoice.check_confirmations()
        self.assertEqual(
            invoice.status, "CONFIRMED"
        )

    def test_invoice_overpaid_confirmed_case(self):
        invoice = self._create_case(
            invoice_amount=Decimal("100.00"),
            tranzes_total_sent_amount=Decimal("125.00"),
            tranzes_count=4,
            tranzes_confirmed_count=4,
        )
        invoice.check_confirmations()
        self.assertEqual(
            invoice.status, "OVERPAID_CONFIRMED"
        )

    def test_invoice_underpaid_confirmed_case(self):
        invoice = self._create_case(
            invoice_amount=Decimal("100.00"),
            tranzes_total_sent_amount=Decimal("75.00"),
            tranzes_count=4,
            tranzes_confirmed_count=4,
        )
        invoice.check_confirmations()
        self.assertEqual(
            invoice.status, "UNDERPAID_CONFIRMED"
        )
