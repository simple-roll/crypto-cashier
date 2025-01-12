USDT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
USDC = "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8"


def get_by_invoice(invoice):
    match(invoice.payment_method.coin_name):
        case "USDT":
            return USDT
        case "USDC":
            return USDC
        case _:
            raise Exception(
                f"Contract address for {invoice.payment_method.coin_name} "
                " does not exists in the tron app"
            )
