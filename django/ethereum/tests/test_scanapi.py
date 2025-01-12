import os
import json
from datetime import datetime, timezone
from decimal import Decimal

from django.test import SimpleTestCase

from ethereum import contracts
from ethereum.scanapi import (
    Client,
)


class TestClient(SimpleTestCase):

    def test_get_erc20_tranzes(self):
        tranzes = Client.get_erc20_tranzes(
            address=os.getenv("ETHEREUM_TEST_ADDRESS"),
            contract=contracts.USDT   
        )
        tranz_list = list(tranzes)
        if len(tranz_list) == 0:
            raise Exception(
                "No any tranzes parsed. "
                "Please make sure you are using ETHEREUM_TEST_ADDRESS "
                "with USDT transactions history"
            )
        for tranz in tranz_list:
            self.assertIsInstance(tranz["txid"], str)
            self.assertIsInstance(tranz["confirmations"], int)
            self.assertIsInstance(tranz["sent_at"], datetime)
            self.assertGreater(
                tranz["sent_at"], 
                datetime(2010, 1, 1, tzinfo=timezone.utc)
            )
            self.assertIsInstance(tranz["amount"], Decimal)

    def test_get_ethereum_coin_tranzes(self):
        tranzes = Client.get_ethereum_coin_tranzes(
            address=os.getenv("ETHEREUM_TEST_ADDRESS"),
        )
        tranz_list = list(tranzes)
        if len(tranz_list) == 0:
            raise Exception(
                "No any tranzes parsed. "
                "Please make sure you are using ETHEREUM_TEST_ADDRESS "
                "with ETH coin transactions history"
            )
        for tranz in tranz_list:
            # print(tranz)
            self.assertIsInstance(tranz["txid"], str)
            self.assertIsInstance(tranz["confirmations"], int)
            self.assertIsInstance(tranz["sent_at"], datetime)
            self.assertGreater(
                tranz["sent_at"], 
                datetime(2010, 1, 1, tzinfo=timezone.utc)
            )
            self.assertIsInstance(tranz["amount"], Decimal)
