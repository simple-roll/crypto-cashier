import importlib

from . import models


def get_chain_app_interface(chain_name):
    chain_app = importlib.import_module(
        f"{chain_name.lower()}.interface"
    )
    return chain_app


def create_address(chain_name):
    chain_app = get_chain_app_interface(chain_name)
    return chain_app.create_address()


def sync_chain_tranzes_for_invoice(invoice):
    chain_app = get_chain_app_interface(
        invoice.payment_method.chain_name
    )
    chain_app.sync_chain_tranzes_for_invoice(invoice)
