from mnemonic import Mnemonic
from bip44 import Wallet
from bip44.utils import get_eth_addr


def create_address():
    mnemo = Mnemonic("english")
    mnemonic_phrase = mnemo.generate(strength=256)
    wallet = Wallet(mnemonic_phrase)
    private_key_bytes, public_key_bytes = wallet.derive_account("eth")
    address = get_eth_addr(public_key_bytes)
    return {
        "address": address, 
        "private_key": private_key_bytes.hex(),
        "mnemonic_phrase": mnemonic_phrase,
    }

