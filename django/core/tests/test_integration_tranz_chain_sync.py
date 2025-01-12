from django.test import TestCase
from django.utils import timezone
from faker import Faker
from faker.providers import date_time
from datetime import timedelta

from core import models
import ethereum.scanapi
from . import (
    factories,
    utils,
)

faker = Faker()
faker.add_provider(date_time)

# Test for core.mixins.InvoiceMixin.find_chain_tranzes
class TranzChainSyncTest(TestCase):
    def test_sync(self):
        now = timezone.now()  # freeze now
        invoice_creation_date = now - timedelta(minutes=5)
        invoice_tranzes_start_date = now - timedelta(minutes=4)
        invoice_tranzes_end_date = now
        invoice_expiration_date = now + timedelta(minutes=60)

        class EtherscanClientMocked(ethereum.scanapi.Client):
            tranzes_before_invoice = 100
            tranzes_during_invoice = 5
            tranzes_after_invoice = 3 

            @classmethod
            def _generate_tranz(cls, **datetime_range):
                return {
                    "txid": faker.uuid4(),
                    "confirmations": faker.pyint(),
                    "sent_at": faker.date_time_between_dates(
                        tzinfo=timezone.get_current_timezone(),
                        **datetime_range
                    ),
                    "amount": faker.pydecimal(
                        left_digits=12,
                        right_digits=12,
                    ),
                }

            @classmethod
            def get_erc20_tranzes(cls, address, contract):
                for _ in range(cls.tranzes_before_invoice):
                    yield cls._generate_tranz(
                        datetime_start=invoice_creation_date - timedelta(days=90),
                        datetime_end=invoice_creation_date - timedelta(minutes=1),
                    )
                for _ in range(cls.tranzes_during_invoice):
                    yield cls._generate_tranz(
                        datetime_start=invoice_tranzes_start_date,
                        datetime_end=invoice_tranzes_end_date,
                    )
                for _ in range(cls.tranzes_after_invoice):
                    yield cls._generate_tranz(
                        datetime_start=invoice_expiration_date, 
                        datetime_end=invoice_expiration_date + timedelta(minutes=5),
                    )

        # Mock scanapi client and create invoice
        ethereum.scanapi.Client = EtherscanClientMocked 
        invoice = factories.InvoiceFactory()
        invoice.created_at = invoice_creation_date
        invoice.expired_at = invoice_expiration_date

        invoice.sync_chain_tranzes()
        self.assertEqual(
            models.Transaction.objects.count(), 5
        )

