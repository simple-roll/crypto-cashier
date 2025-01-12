import requests
import hashlib
from decimal import Decimal


class CallbackClient:
    def __init__(
        self, 
        invoice: "core.models.Invoice", 
    ):
        self._params = {
            "is_payment_successful": invoice.is_successful,
            "merchant_uuid": str(invoice.merchant.uuid),
            "order_id": invoice.order_id,
            "order_amount": str(invoice.amount),
            "payment_status": invoice.status,
            "coin_name": invoice.payment_method.coin_name,
            "chain_name": invoice.payment_method.chain_name,
            "chain_txids": [
                tranz.txid 
                for tranz in invoice.transactions.all()
            ],
        }

        if invoice.amount_confirmed:
            amount_underpaid = invoice.amount - invoice.amount_confirmed
            amount_overpaid = invoice.amount_confirmed - invoice.amount
            self._params.update({
                "amount_confirmed": str(
                    invoice.amount_confirmed
                ),
                "amount_underpaid": str(
                    amount_underpaid if amount_underpaid > 0 else 0 
                ),
                "amount_overpaid": str(
                    amount_overpaid if amount_overpaid > 0 else 0 
                ),
            })
        else:
            self._params.update({
                "amount_confirmed": None,
                "amount_underpaid": None,
                "amount_overpaid": None,
            })

        self._sign_key = invoice.merchant.sign_key
        self._url = invoice.merchant.callback_url

    def _sign_params(self):
        p = self._params
        sum_source = ":".join([
            self._sign_key,
            str(p['merchant_uuid']),
            str(p['chain_name']),
            str(p['coin_name']),
            str(p["order_amount"]),
        ]).encode()
        md5 = hashlib.md5(sum_source).hexdigest()
        self._params["sign"] = md5

    def _send_request(self):
        self._sign_params()
        attempts = 5
        for _ in range(attempts):
            try:
                response = requests.post(self._url, json=self._params)
                if response.status_code == 200:
                    return response.json()
            except requests.RequestException as e:
                log.exception(f"Sending notification failed: {e}")
        raise Exception(
            "Cannot send notification for {invoice} "
            "because callback_url: {self._url} is not available "
            "after 5 tries"
        )

    def send(self) -> bool:
        return self._send_request()
