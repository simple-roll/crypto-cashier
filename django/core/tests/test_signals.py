from django.test import TestCase
from django.utils import timezone
import factory
from factory.faker import faker

from core import models
from . import (
    factories,
    utils,
)


# Test for core.mixins.InvoiceMethodsMixin.find_chain_tranzes
class GetFreeAddressTest(TestCase):
    def setUp(self):
        pass

    def test(self):
        fake = faker.Faker()
        invoice = models.Invoice.objects.create(
            merchant=factories.MerchantFactory(),
            expired_at=fake.future_datetime(
                tzinfo=timezone.get_current_timezone()
            ),
            amount=fake.pydecimal(
                left_digits=12,
                right_digits=12,
            ),
            # customer=factories.CustomerFactory(),
            payment_method=factories.PaymentMethodFactory(),
            status="UNPAID",
        )
        self.assertTrue(invoice.address is not None)
        self.assertTrue(invoice.address.qr_image is not None)
        self.assertEqual(invoice.address.status, "BUSY")
        self.assertNotEquals(invoice.address.reserved_until, None)
