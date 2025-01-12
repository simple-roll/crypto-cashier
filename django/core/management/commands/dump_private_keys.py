import json
from django.db.models import Q
from django.core.management.base import BaseCommand
from core.models import Address


class Command(BaseCommand):
    help = 'Dump addresses to JSON'

    def _get_addrs_with_privkeys(self):
        for addr in Address.objects.filter(
            Q(
                private_key__isnull=False
            ) | Q(
                mnemonic_phrase__isnull=False
            )
        ):
            yield {
                "address": addr.address,
                "private_key": addr.private_key,
                "mnemonic_phrase": addr.mnemonic_phrase,
            }

    def handle(self, *args, **kwargs):
        data = list(self._get_addrs_with_privkeys())
        self.stdout.write(
            json.dumps(data, indent=4)
        )
