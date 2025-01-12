import logging

from core.models import (
    Invoice
)
from . import (
    chain,
    scanapi,
    contracts,
)

log = logging.getLogger("core")


def sync_chain_tranzes_for_invoice(invoice: Invoice):
    match invoice.payment_method.coin_name:
        case "USDT" | "USDC":
            tranzes = scanapi.Client.get_trc20_tranzes(
                address=invoice.address.address,
                contract=contracts.get_by_invoice(invoice),
            )
        case "TRX":
            tranzes = scanapi.Client.get_tron_coin_tranzes(
                address=invoice.address.address
            )
        case _:
            raise Exception(
                f"Unsupported coin name {invoice.payment_method.coin_name} "
                "in tron app"
            )
    tranz_list = list(tranzes)
    if len(tranz_list) == 0:
        log.debug(
            f"No any tranzes for {invoice} in the Tron chain"
        )
    for tranz in tranz_list:
        if invoice.is_my_tranz(tranz["sent_at"]):
            log.debug(
                f"Update {invoice} tranz with data {tranz}"
                "in the Tron chain"
            )
            invoice.update_or_create_tranz(**tranz)


def create_address():
    return chain.create_address()
