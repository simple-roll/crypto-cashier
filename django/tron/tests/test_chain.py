from django.test import SimpleTestCase
from tron.chain import (
    create_address,
)


class TestCreateAddress(SimpleTestCase):
    def test_1(self):
        address: dict = create_address()
        self.assertEqual(
            ["address", "private_key", "mnemonic_phrase"],
            list(address.keys())
        )

