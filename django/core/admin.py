from django.contrib import admin
from django.conf import settings
from django_celery_results.admin import TaskResult, GroupResult
from django_celery_beat.admin import (
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
    PeriodicTask,
)
from django.utils.html import format_html
from . import models

if settings.CELERY_IGNORE_RESULT is True:
    # Disable Celery tasks results pages
    admin.site.unregister(TaskResult)
    admin.site.unregister(GroupResult)

if settings.CELERY_DISABLE_BEAT_ADMIN is True:
    admin.site.unregister(SolarSchedule)
    admin.site.unregister(ClockedSchedule)
    admin.site.unregister(PeriodicTask)
    admin.site.unregister(IntervalSchedule)
    admin.site.unregister(CrontabSchedule)


class PaymentMethodInline(admin.TabularInline):
    model = models.PaymentMethod
    extra = 0
    fields = (
        "coin_name",
        "chain_name",
        "confirmations_required",
        "is_enabled",
    )
    readonly_fields = (
        "chain_name",
        "coin_name",
    )

    def has_add_permission(self, request, *args, **kwargs):
        return False

    def has_delete_permission(self, request, *args, **kwargs):
        return False


@admin.register(models.Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("name", "uuid", "callback_url")
    search_fields = ("name", "uuid")
    readonly_fields = ("uuid",)
    inlines = [PaymentMethodInline]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not obj:
            fields.remove('uuid')
            fields.remove('sign_key')
        return fields

    def get_inlines(self, request, obj=None):
        if obj:
            return [PaymentMethodInline]
        return []


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "created_at",
        "expired_at",
        # "order_id",
        # "product_name",
        "merchant",
        # "customer",
        "amount",
        "amount_confirmed",
        "payment_method",
        "status",
        "is_processing",
        # "is_notified",
        "is_successful",
    )
    list_filter = (
        "is_processing",
        "is_successful",
        "payment_method__chain_name",
        "payment_method__coin_name",
        "status",
    )
    search_fields = (
        "order_id",
        "product_name",
        "merchant__name",
        # "customer__name"
    )
    readonly_fields = (
        "uuid",
        "created_at",
        "merchant",
        "payment_method",
        "amount",
        "amount_confirmed",
        "is_processing",
        "is_notified",
        "is_successful",
        "address",
        "order_id",
        "product_name",
        "status",
        "payment_success_url",
        "payment_failure_url",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "created_at",
                    "expired_at",
                    "order_id",
                    "product_name",
                    "merchant",
                    # "customer",
                    "amount",
                    "amount_confirmed",
                    "payment_method",
                    "address",
                    "status",
                    "payment_success_url",
                    "payment_failure_url",
                    "is_processing",
                    "is_notified",
                    "is_successful",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return False


class HasStoredAddressKeysFilter(admin.SimpleListFilter):
    title = 'Has Stored Keys'
    parameter_name = 'has_stored_keys'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(
                mnemonic_phrase__isnull=False
            ) | queryset.filter(
                private_key__isnull=False
            )
        if self.value() == 'no':
            return queryset.filter(
                mnemonic_phrase__isnull=True,
                private_key__isnull=True
            )
        return queryset


@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'address',
        'key_security_status',
        'status',
        'chain_name',
        'created_at',
        'reserved_until',
    )
    list_filter = (
        'status',
        HasStoredAddressKeysFilter,
    )

    def key_security_status(self, obj):
        if obj.mnemonic_phrase or obj.private_key:
            return format_html(
                '<span style="color: red;" title="'
                'Private key and mnemonic phrase '
                'stored in the database'
                '">⚠️</span>'
            )
        return format_html(
            '<span style="color: green;">✔️</span>'
        )
    key_security_status.short_description = 'Security'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (
                'created_at',
                'address',
                'chain_name',
                'qr_image'
            )
        return []

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj is None:
            [
                fields.remove(field)
                for field in (
                    "private_key",
                    "mnemonic_phrase",
                    "qr_image",
                    "status",
                    'reserved_until',
                )
            ]
        return [
            field
            for field in fields
            if field not in ("private_key", "mnemonic_phrase")
        ]

    def changelist_view(self, request, extra_context=None):
        addresses_with_keys = self.model.objects.filter(
            mnemonic_phrase__isnull=False
        ) | self.model.objects.filter(
            private_key__isnull=False
        )
        if addresses_with_keys.exists():
            self.message_user(
                request,
                format_html(
                    f"Warning: There are {addresses_with_keys.count()} addresses with stored "
                    "private keys and mnemonic phrase in the database. <br><br>"
                    "1. Dump all keys keys and mnemonics using command: <br>"
                    "<strong>./manage.sh dump_private_keys`</strong><br><br>"
                    "2. Copy command output json and paste in safe place. <br><br>"
                    "3. Then delete them with command: <br>"
                    "<strong>./manage.sh delete_private_keys</strong><br><br>"
                    "See README.md for more info"
                ),
                level="WARNING",
            )
        return super().changelist_view(request, extra_context=extra_context)
