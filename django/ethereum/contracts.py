USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"


def get_by_invoice(invoice):
    match(invoice.payment_method.coin_name):
        case "USDT":
            return USDT
        case "USDC":
            return USDC
        case _:
            raise Exception(
                f"Contract address for {invoice.payment_method.coin_name} "
                " does not exists in the ethereum app"
            )
