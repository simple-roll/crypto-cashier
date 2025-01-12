import os
from .models import Merchant, PaymentMethod


def create_payment_methods(merchant: Merchant):
    payment_methods = [
        (pm.chain_name, pm.coin_name)
        for pm in merchant.payment_methods.all()
    ]

    #
    # Ethereum chain
    #
    if ("ETHEREUM", "ETH") not in payment_methods:
        PaymentMethod.objects.create(
            merchant=merchant,
            coin_name="ETH",
            chain_name="ETHEREUM",
            standard="NATIVE",
            confirmations_required=10,
            amount_decimal_rounding=6,
            is_enabled=(
                os.getenv("ETHEREUM_NATIVE_COIN_ENABLED") == "true"
            )
        )
    if ("ETHEREUM", "USDT") not in payment_methods:
        PaymentMethod.objects.create(
            merchant=merchant,
            coin_name="USDT",
            chain_name="ETHEREUM",
            standard="ERC20",
            confirmations_required=10,
            amount_decimal_rounding=2,
            is_enabled=(
                os.getenv("ETHEREUM_USDT_ERC20_ENABLED") == "true"
            )
        )
    if ("ETHEREUM", "USDC") not in payment_methods:
        PaymentMethod.objects.create(
            merchant=merchant,
            coin_name="USDC",
            chain_name="ETHEREUM",
            standard="ERC20",
            confirmations_required=10,
            amount_decimal_rounding=2,
            is_enabled=(
                os.getenv("ETHEREUM_USDC_ERC20_ENABLED") == "true"
            )
        )

    #
    # Tron chain
    #
    if ("TRON", "TRX") not in payment_methods:
        PaymentMethod.objects.create(
            merchant=merchant,
            coin_name="TRX",
            chain_name="TRON",
            standard="NATIVE",
            confirmations_required=10,
            amount_decimal_rounding=4,
            is_enabled=(
                os.getenv("TRON_NATIVE_COIN_ENABLED") == "true"
            )
        )

    if ("TRON", "USDT") not in payment_methods:
        PaymentMethod.objects.create(
            merchant=merchant,
            coin_name="USDT",
            chain_name="TRON",
            standard="TRC20",
            confirmations_required=10,
            amount_decimal_rounding=2,
            is_enabled=(
                os.getenv("TRON_USDT_TRC20_ENABLED") == "true"
            )
        )

    if ("TRON", "USDC") not in payment_methods:
        PaymentMethod.objects.create(
            merchant=merchant,
            coin_name="USDC",
            chain_name="TRON",
            standard="TRC20",
            confirmations_required=10,
            amount_decimal_rounding=2,
            is_enabled=(
                os.getenv("TRON_USDC_TRC20_ENABLED") == "true"
            )
        )
