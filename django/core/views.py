import re
from decimal import Decimal
from django import forms
from django.utils import timezone
from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError

from . import models


def validate_uuid(value):
    value = str(value)
    if not re.match(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', value):
        raise ValidationError(
            "Merchant UUID is invalid"
        )


def validate_alphanumeric_dash_underscore(value):
    if not re.match(r'^[\w-]+$', value):
        raise ValidationError(
            'This field can only contain letters, digits, hyphens, '
            'and underscores.'
        )


def validate_alphanumeric_dash(value):
    if not re.match(r'^[a-zA-Z0-9-]+$', value):
        raise ValidationError(
            'This field can only contain letters, digits, and hyphens.'
        )


def validate_merchant_uuid(value):
    validate_uuid(value)
    if not models.Merchant.objects.filter(
        uuid=value
    ).exists():
        raise ValidationError(
            f"Merchant {value} does not exists"
        )


class CreateInvoiceForm(forms.Form):
    merchant_uuid = forms.UUIDField(
        validators=[validate_merchant_uuid],
        widget=forms.HiddenInput(),
    )
    order_id = forms.CharField(
        max_length=255,
        validators=[validate_alphanumeric_dash_underscore],
        widget=forms.HiddenInput(),
    )
    product_name = forms.CharField(
        max_length=255,
        validators=[validate_alphanumeric_dash],
        widget=forms.HiddenInput(),
    )
    amount = forms.DecimalField(
        max_digits=24,
        decimal_places=12,
        widget=forms.HiddenInput(),
    )
    coin_name = forms.CharField(
        max_length=4,
        validators=[validate_alphanumeric_dash],
        widget=forms.HiddenInput(),
    )
    chain_name = forms.CharField(
        max_length=8,
        validators=[validate_alphanumeric_dash],
        widget=forms.HiddenInput(),
    )
    payment_success_url = forms.URLField(
        required=False,
        widget=forms.HiddenInput()
    )
    payment_failure_url = forms.URLField(
        required=False,
        widget=forms.HiddenInput()
    )
    # customer_email = forms.EmailField()
    comment = forms.CharField(
        max_length=255,
        validators=[validate_alphanumeric_dash],
        required=False,
        widget=forms.HiddenInput()
    )

    def clean_payment_success_url(self):
        url = self.cleaned_data.get('payment_success_url')
        return url or None

    def clean_payment_failure_url(self):
        url = self.cleaned_data.get('payment_failure_url')
        return url or None

    def clean(self):
        cleaned_data = super().clean()

        merchant_uuid = cleaned_data.get("merchant_uuid")
        if merchant_uuid is None:
            # Was validation error with merchant_uuid field
            return

        merchant = models.Merchant.objects.get(
            uuid=merchant_uuid
        )

        coin_name = cleaned_data.get("coin_name")
        chain_name = cleaned_data.get("chain_name")
        if coin_name and chain_name:
            if not merchant.is_payment_method_available(
                chain_name=chain_name,
                coin_name=coin_name,
            ):
                self.add_error(
                    'coin_name',
                    f"Payment with coin '{coin_name}' on chain "
                    f"'{chain_name}' is not supported or disabled"
                )
        else:
            self.add_error(
                "Have to set both: coin_name and chain_name"
            )


class CreateInvoice(View):

    def get(self, request, *args, **kwargs):
        form = CreateInvoiceForm(request.GET)
        if form.is_valid():
            d = form.cleaned_data

            existing_invoice = self._get_existing_invoice(d)
            if existing_invoice is not None:
                return redirect(
                    "core:invoice",
                    invoice_uuid=existing_invoice.uuid,
                )

            merchant = models.Merchant.objects.get(
                uuid=d["merchant_uuid"]
            )
            payment_method = merchant.get_payment_method(
                coin_name=d["coin_name"],
                chain_name=d["chain_name"],
            )
        else:
            merchant = None
            payment_method = None

        return render(
            request,
            "core/create_invoice.html",
            {
                "form": form,
                "merchant": merchant,
                "payment_method": payment_method
            }
        )

    def post(self, request, *args, **kwargs):
        form = CreateInvoiceForm(request.POST)
        if form.is_valid():
            # Handle case when customer push browser <Back> button
            # to creating invocie page and push <Pay> again
            invoice = self._get_existing_invoice(form.cleaned_data)
            if invoice is None:
                invoice = self._create_new_invoice(form.cleaned_data)
            return redirect(
                "core:invoice",
                invoice_uuid=invoice.uuid,
            )
        else:
            return render(
                request,
                "core/create_invoice.html",
                {
                    "form": form,
                    "merchant": None,
                }
            )

    def _get_existing_invoice(
        self,
        cleaned_data: dict
    ):
        d = cleaned_data
        filter = {
            "order_id": d["order_id"],
            "amount": Decimal(d["amount"]),
            "payment_method__coin_name": d["coin_name"],
            "payment_method__chain_name__iexact": d["chain_name"],
            "is_processing": True,
        }
        if models.Invoice.objects.filter(**filter).exists():
            return models.Invoice.objects.get(**filter)
        else:
            return None

    def _create_new_invoice(
        self,
        cleaned_data: dict
    ):
        d = cleaned_data
        merchant = models.Merchant.objects.get(
            uuid=d["merchant_uuid"]
        )
        payment_method = merchant.get_payment_method(
            coin_name=d["coin_name"],
            chain_name=d["chain_name"],
        )
        # customer, created = models.Customer.objects.get_or_create(
        #     email=d["customer_email"]
        # )
        expired_at = timezone.now() + payment_method.expiration
        invoice = models.Invoice.objects.create(
            merchant=merchant,
            # customer=customer,
            expired_at=expired_at,
            order_id=d["order_id"],
            product_name=d["product_name"],
            payment_method=payment_method,
            amount=d["amount"],
            payment_success_url=d["payment_success_url"],
            payment_failure_url=d["payment_failure_url"],
            status="UNPAID"
        )
        return invoice


class Invoice(View):
    def get(self, request, invoice_uuid):
        try:
            invoice = models.Invoice.objects.get(
                uuid=invoice_uuid,
            )
        except models.Invoice.DoesNotExist:
            return HttpResponse("Wrong invoice UUID")

        return render(
            request,
            "core/invoice.html",
            {
                "invoice": invoice,
                "merchant": invoice.merchant,
                "payment_method": invoice.payment_method,
                "seconds_left": self._calc_timer_seconds_left(
                    invoice.expired_at
                ),
            }
        )

    def _calc_timer_seconds_left(self, expired_at: "datetime"):
        now = timezone.now()
        time_left = expired_at - now
        seconds_left = int(time_left.total_seconds())
        return seconds_left
