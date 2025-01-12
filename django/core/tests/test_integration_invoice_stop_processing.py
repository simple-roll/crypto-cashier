import json
from django.test import TestCase
from decimal import Decimal

from . import factories


POST_REQUEST_TESTER = "https://httpbin.org/post"


class InvoiceStopProcessingTest(TestCase):
    def test_stop_processing(self):
        invoice = factories.InvoiceFactory(
            merchant__callback_url=POST_REQUEST_TESTER,
            status="CONFIRMED",
        )
        invoice.amount_confirmed = invoice.amount

        invoice.stop_processing()
        response_json = invoice.send_notification()

        data = json.loads(response_json["data"])
        self.assertTrue(invoice.is_notified)
        self.assertFalse(invoice.is_processing)
        self.assertTrue(data["is_payment_successful"])
        self.assertEqual(
            Decimal(data["amount_overpaid"]), 
            invoice.amount_confirmed - invoice.amount
        )
        self.assertEqual(invoice.address.reserved_until, None)
        self.assertEqual(invoice.address.status, "FREE")
