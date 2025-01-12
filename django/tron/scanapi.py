import os
import json
from time import sleep

from core.scanapi import (
    ClientBase,
    Converter,
)


API_DOMAIN = "apilist.tronscanapi.com"


class Parser:
    converter = Converter

    @classmethod
    def parse_tron_coin_tranzes(
        cls, 
        response: dict, 
        address: str,
        current_block: int
    ):
        tranz_list = response["data"]
        # print(response)
        for tranz in tranz_list:
            if tranz["transferToAddress"] != address:
                continue
            if tranz["riskTransaction"] == True:
                continue
            if tranz["amount"] < 10:
                # Skip dust transactions
                continue
            sent_at = cls.converter.timestamp_to_date(tranz["timestamp"])
            amount = cls.converter.chain_value_to_amount(
                tranz["amount"], tranz["tokenInfo"]["tokenDecimal"]
            )
            confirmations = current_block - tranz["block"]
            yield {
                "txid": tranz["transactionHash"],
                "confirmations": confirmations,
                "sent_at": sent_at,
                "amount": amount,
            }

    @classmethod
    def parse_trc20_tranzes(
        cls, 
        response: dict, 
        address: str,
        contract: str,
        current_block: int
    ):
        tranz_list = response["token_transfers"]
        for tranz in tranz_list:
            if tranz["to_address"] != address:
                continue
            if tranz["contract_address"].lower() != contract.lower():
                continue
            if tranz["quant"] == "0":
                continue
            sent_at = cls.converter.timestamp_to_date(tranz["block_ts"])
            amount = cls.converter.chain_value_to_amount(
                tranz["quant"], tranz["tokenInfo"]["tokenDecimal"]
            )
            confirmations = current_block - tranz["block"]
            yield {
                "txid": tranz["transaction_id"],
                "confirmations": confirmations,
                "sent_at": sent_at,
                "amount": amount,
            }


class Client(ClientBase):
    url_netloc = API_DOMAIN
    headers = {
        "TRON-PRO-API-KEY": os.getenv("TRONSCAN_API_KEY")
    }
    parser = Parser

    @classmethod
    def _send_request(cls, url): 
        return cls.send_request(url, cls.headers)

    @classmethod
    def _get_current_block_number(cls) -> int:
        path = "api/block/statistic"
        url = cls.build_url(path, params={})
        response = cls._send_request(url)
        return int(response["whole_block_count"])

    @classmethod
    def get_trc20_tranzes(cls, address: str, contract: str):
        path = "api/token_trc20/transfers"
        params = {
            "limit": "20",
            "start": "0",
            "toAddress": address,
            "contract_address": contract,
            "start_timestamp": "",
            "end_timestamp": "",
            "confirm": "true",
            "filterTokenValue": "1",
        }
        url = cls.build_url(path, params)
        response = cls._send_request(url)
        current_block = cls._get_current_block_number()
        return cls.parser.parse_trc20_tranzes(
            response, address, contract, current_block
        )
        
    @classmethod
    def get_tron_coin_tranzes(cls, address: str):
        path = "api/transfer"
        params = {
            "limit": "20",
            "start": "0",
            "toAddress": address,
            "address": address,
            # "tokens": "TRX",
            "start_timestamp": "",
            "end_timestamp": "",
            # "filterTokenValue": "1",
        }
        url = cls.build_url(path, params)
        response = cls._send_request(url)
        current_block = cls._get_current_block_number()
        return cls.parser.parse_tron_coin_tranzes(
            response, address, current_block
        )

