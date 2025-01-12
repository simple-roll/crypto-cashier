import os
from time import sleep
import requests
import logging
from datetime import datetime
import pytz
from decimal import Decimal
from urllib.parse import urlencode, urlunparse


log = logging.getLogger("core")


class Converter:
    @staticmethod
    def chain_value_to_amount(value, decimal_places: int):
        return Decimal(str(value)) / Decimal(10**decimal_places)

    def timestamp_to_date(timestamp):
        try:
            timestamp = int(timestamp)
            if len(str(timestamp)) == 13:
                timestamp //= 1000
            return datetime.fromtimestamp(
                timestamp, 
                pytz.UTC
            )
        except (ValueError, TypeError):
            return None


class ClientBase:
    @classmethod
    def send_request(cls, url:str, headers: dict = {}):
        attempts = 5
        for _ in range(attempts):
            try:
                response = requests.get(url, headers)
            except requests.exceptions.RequestException as e:
                log.exception(e)
                sleep(5)
                continue

            if response.ok:
                return response.json()
            else:
                raise Exception(
                    f"Chainscan API response not ok: {response.status_code}"
                )

        raise Exception(
            "Cannot complete request after 5 attempts"
        )

    @classmethod
    def build_url(cls, path: str, params: dict):
        return urlunparse([
            "https",
            cls.url_netloc,
            path,
            "",
            urlencode(params),
            ""
        ])

