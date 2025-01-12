from django.core.management.base import BaseCommand
from django.db.models import Q
from core.models import Address


class Command(BaseCommand):
    help = 'Delete all private keys and mnemonic phrases from addresses'

    def handle(self, *args, **options):
        self.stdout.write(
            "Warning: You should run the `dump_private_keys` command "
            "before proceeding and ensure all private keys are saved "
            "in a safe place. Continue? [Y/n]: ",
            ending=''
        )
        confirm = input().strip().lower()
        if confirm not in ('y', 'yes', ''):
            self.stdout.write("Operation cancelled.")
            return

        addresses_with_keys = Address.objects.filter(
            Q(
                private_key__isnull=False
            ) | Q(
                mnemonic_phrase__isnull=False
            )
        )

        if not addresses_with_keys.exists():
            self.stdout.write(
                "No addresses with private keys or mnemonic phrases found. "
                "It's absolutely safe here now"
            )
            return

        addresses_with_keys.update(
            private_key=None,
            mnemonic_phrase=None
        )

        self.stdout.write(
            self.style.SUCCESS(
                "All private keys and mnemonic phrases have been deleted. "
                "It's absolutely safe here now"
            )
        )
