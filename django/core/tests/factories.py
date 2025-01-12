import factory
from factory.django import DjangoModelFactory
from django.utils import (
    timezone
)

from core import models


class MerchantFactory(DjangoModelFactory):
    class Meta:
        model = models.Merchant

    name = factory.Faker('word')
    callback_url = factory.Faker('url')
    sign_key = factory.Faker('pystr')


class PaymentMethodFactory(DjangoModelFactory):
    class Meta:
        model = models.PaymentMethod

    merchant = factory.SubFactory(MerchantFactory)
    coin_name = "USDT"
    chain_name = "ETHEREUM"
    standard = "ERC20"
    is_enabled = factory.Faker('boolean')
    confirmations_required = factory.Faker('random_int', min=1, max=10)


# class CustomerFactory(DjangoModelFactory):
#     class Meta:
#         model = models.Customer

#     email = factory.Faker('email')


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = models.Address

    address = factory.Faker('ipv4')
    chain_name = "ETHEREUM"
    # reserved_by_customer = factory.SubFactory(CustomerFactory)
    reserved_until = factory.Faker(
        'future_datetime',
        tzinfo=timezone.get_current_timezone(),
    )
    private_key = factory.Faker('md5')


class InvoiceFactory(DjangoModelFactory):
    class Meta:
        model = models.Invoice

    order_id = factory.Faker('pystr')
    expired_at = factory.Faker(
        'future_datetime',
        tzinfo=timezone.get_current_timezone(),
    )
    merchant = factory.SubFactory(MerchantFactory)
    # customer = factory.SubFactory(CustomerFactory)
    amount = factory.Faker(
        'pydecimal',
        left_digits=12,
        right_digits=12,
        positive=True
    )
    payment_method = factory.SubFactory(PaymentMethodFactory)
    address = factory.SubFactory(AddressFactory)
    status = factory.Faker(
        'random_element',
        elements=[
            choice[0]
            for choice in models.InvoiceStatusChoice.choices
        ]
    )


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = models.Transaction

    sent_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone()
    )
    invoice = factory.SubFactory(InvoiceFactory)
    txid = factory.Faker('uuid4')
    # is_ignored = False
    amount = factory.Faker(
        'pydecimal',
        left_digits=12,
        right_digits=12,
        positive=True
    )
    # status = factory.Faker(
    #     'random_element',
    #     elements=[
    #         choice[0]
    #         for choice in models.TransactionStatusChoices.choices
    #     ]
    # )
