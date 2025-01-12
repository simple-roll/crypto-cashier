from mnemonic import Mnemonic
from tronpy.keys import PrivateKey
from tronpy import Tron


def create_address():
    out = Tron().generate_address_with_mnemonic()
    return {
        "address": out[0]["base58check_address"], 
        "private_key": out[0]["private_key"],
        "mnemonic_phrase": out[1],
    }

