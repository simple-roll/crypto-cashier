import os
from time import sleep
import json

from core.scanapi import (
    ClientBase,
    Converter,
)


API_DOMAIN = "api.etherscan.io"


class Parser:
    converter = Converter

    @classmethod
    def parse_erc20_tranzes(
        cls, 
        response: dict,
        address: str,
        contract: str
    ):
        tranz_list = response["result"]
        for tranz in tranz_list:
            if tranz["to"] != address:
                continue
            if tranz["contractAddress"].lower() != contract.lower():
                continue
            if tranz["value"] == "0":
                continue
            sent_at = cls.converter.timestamp_to_date(tranz["timeStamp"])
            amount = cls.converter.chain_value_to_amount(
                tranz["value"], 6
            )
            yield {
                "txid": tranz["hash"],
                "confirmations": int(tranz["confirmations"]),
                "sent_at": sent_at,
                "amount": amount,
            }

    @classmethod
    def parse_ethereum_coin_tranzes(
        cls, 
        response: dict,
        address: str
    ):
        tranz_list = response["result"]
        for tranz in tranz_list:
            if tranz["to"] != address:
                continue
            if tranz["contractAddress"] != "":
                continue
            if tranz["value"] == "0":
                continue
            amount = cls.converter.chain_value_to_amount(
                tranz["value"], 18
            )
            sent_at = cls.converter.timestamp_to_date(tranz["timeStamp"])
            yield {
                "txid": tranz["hash"],
                "confirmations": int(tranz["confirmations"]),
                "sent_at": sent_at,
                "amount": amount,
            }


class Client(ClientBase):
    url_netloc = API_DOMAIN
    apikey = os.getenv("ETHERSCAN_API_KEY")
    parser = Parser

    @classmethod
    def get_erc20_tranzes(cls, address, contract):
        # Returns the list of ERC-20 tokens transferred by an address, with optional filtering by token contract.
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": contract,
            "address": address,
            "apikey": cls.apikey,
            # "page": 1,
            # "offset": 100,
            # "startblock": 0,
            # "endblock": 27025780,
        }
        url = cls.build_url(path="api", params=params)
        response = cls.send_request(url)
        return cls.parser.parse_erc20_tranzes(
            response, address, contract
        )

    @classmethod
    def get_ethereum_coin_tranzes(cls, address):
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "apikey": cls.apikey,
            "startblock": "0",
            "endblock": "99999999",
            "page": "1",
            "offset": "10",
            "sort": "asc",
        }
        url = cls.build_url(path="api", params=params)
        response = cls.send_request(url)
        return cls.parser.parse_ethereum_coin_tranzes(
            response, address
        )
