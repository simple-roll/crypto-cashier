import uuid
from django.db import models
from datetime import timedelta
from encrypted_model_fields.fields import EncryptedCharField

from . import mixins


# class TransactionStatusChoices(models.TextChoices):
#     CONFIRMATION = "CONFIRMATION", "CONFIRMATION"
#     CONFIRMED = "CONFIRMED", "CONFIRMED"
#     FAILED = "FAILED", "FAILED"


class AddressStatusChoice(models.TextChoices):
    FREE = "FREE", "FREE"
    BUSY = "BUSY", "BUSY"
    ISSUE = "ISSUE", "ISSUE"
    DISABLED = "DISABLED", "DISABLED"


class InvoiceStatusChoice(models.TextChoices):
    UNPAID = "UNPAID", "Unpaid"
    PAID = "PAID", "Paid and confirming"
    CONFIRMED = "CONFIRMED", "Confirmed"
    UNDERPAID = "UNDERPAID", "Underpaid"
    OVERPAID = "OVERPAID", "Overpaid and confirming"
    UNDERPAID_CONFIRMED = "UNDERPAID_CONFIRMED", "Underpaid and Confirmed"
    OVERPAID_CONFIRMED = "OVERPAID_CONFIRMED", "Overpaid and Confirmed"
    CANCELED = "CANCELED", "Canceled"
    EXPIRED = "EXPIRED", "Expired"


class PaymentMethodChainChoice(models.TextChoices):
    ETHEREUM = "ETHEREUM", "Ethereum"
    TRON = "TRON", "Tron"


class PaymentMethodCoinChoice(models.TextChoices):
    ETH = "ETH", "ETH"
    TRX = "TRX", "TRX"
    USDT = "USDT", "USDT"
    USDC = "USDC", "USDC"


class PaymentMethodStandartChoice(models.TextChoices):
    NATIVE = "NATIVE", "Native"
    ERC20 = "ERC20", "ERC20"
    TRC20 = "TRC20", "TRC20"


class Merchant(models.Model, mixins.MerchantMixin):
    name = models.CharField(
        help_text=(
            "Name of shop or service"
        )
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        blank=True,
        help_text=(
            "Merchant external ID"
        )
    )
    callback_url = models.URLField(
        help_text=(
            "URL for receiving POST callbacks of payment results"
        )
    )
    sign_key = EncryptedCharField(
        max_length=64,
        blank=True,
        help_text=(
            "Key for signing requests"
        )
    )

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="payment_methods",
    )
    coin_name = models.CharField(
        max_length=50,
        choices=PaymentMethodCoinChoice.choices
    )
    chain_name = models.CharField(
        max_length=50,
        choices=PaymentMethodChainChoice.choices
    )
    standard = models.CharField(
        choices=PaymentMethodStandartChoice.choices
    )
    is_enabled = models.BooleanField(default=False)
    confirmations_required = models.IntegerField()
    expiration = models.DurationField(
        default=timedelta(minutes=60)
    )
    amount_decimal_rounding = models.IntegerField(default=8)
    # withdrawal_address = models.CharField(
    #     max_length=255
    #     null=True,
    #     default=None
    # )
    # withdrawal_chain_fee_limit = models.DecimalField(
    #     max_digits=24,
    #     decimal_places=12
    #     null=True,
    #     default=None
    # )

    def __str__(self):
        return self.chain_name + ":" + self.coin_name


# class Customer(models.Model):
#     registered_at = models.DateTimeField(auto_now_add=True)
#     email = models.EmailField()

#     def __str__(self):
#         return self.email


class Address(models.Model, mixins.AddressMixin):
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=10,
        choices=AddressStatusChoice.choices,
        default="FREE"
    )
    chain_name = models.CharField(
        max_length=50,
        choices=PaymentMethodChainChoice.choices,
    )
    # payment_method = models.ForeignKey(
    #     PaymentMethod,
    #     related_name="addresses",
    #     on_delete=models.CASCADE
    # )
    # reserved_by_customer = models.ForeignKey(
    #     Customer,
    #     on_delete=models.CASCADE,
    #     null=True, blank=True,
    # )
    reserved_until = models.DateTimeField(null=True, blank=True)
    private_key = EncryptedCharField(max_length=64)
    mnemonic_phrase = EncryptedCharField(max_length=512)
    qr_image = models.ImageField()

    def __str__(self):
        return self.address


class Invoice(models.Model, mixins.InvoiceMixin):
    objects = models.Manager()  # The default manager.
    processing = mixins.InvoiceProcessingManager()

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    order_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="invoices"
    )
    # customer = models.ForeignKey(
    #     Customer,
    #     on_delete=models.CASCADE,
    #     related_name="invoices"
    # )
    amount = models.DecimalField(
        max_digits=24,
        decimal_places=12
    )
    amount_confirmed = models.DecimalField(
        max_digits=24,
        decimal_places=12,
        null=True, blank=True
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        related_name="payment_methods",
        on_delete=models.CASCADE
    )
    address = models.ForeignKey(
        Address,
        related_name="invoices",
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=50,
        choices=InvoiceStatusChoice.choices
    )
    payment_success_url = models.URLField(
        null=True, blank=True
    )
    payment_failure_url = models.URLField(
        null=True, blank=True
    )
    is_processing = models.BooleanField(default=True)
    is_notified = models.BooleanField(default=False)
    is_successful = models.BooleanField(null=True, default=None)

    def __str__(self):
        # return f"Invoice {self.id} for {self.customer}"
        return f"Invoice {self.id}"


class Transaction(models.Model, mixins.TransactionMixin):
    found_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField()
    # is_ignored = models.BooleanField(default=False)
    txid = models.CharField(max_length=100)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True, blank=True,  # is_ignored case
    )
    # status = models.CharField(
    #     TransactionStatusChoices.choices
    # )
    confirmations = models.IntegerField(default=0)
    amount = models.DecimalField(
        max_digits=24,
        decimal_places=12
    )

    def __str__(self):
        return self.txid
