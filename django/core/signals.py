import secrets
from django.db.models.signals import (
    post_save,
    pre_save,
)
from django.dispatch import receiver
import logging
import segno

from . import (
    models,
    chain,
)


log = logging.getLogger("core")


@receiver(pre_save, sender=models.Address)
def create_new_chain_address(sender, instance, *args, **kwargs):
    if instance.is_new_record():
        if instance.address == "":
            # Generate new address
            address = chain.create_address(instance.chain_name)
            instance.address = address["address"]
            instance.private_key = address["private_key"]
            instance.mnemonic_phrase = address["mnemonic_phrase"]

        image_path = f"media/qr/{instance.address}.png"
        qrcode = segno.make_qr(f"{instance.address}")
        qrcode.save(image_path, scale=6, border=0)
        instance.qr_image = image_path


@receiver(pre_save, sender=models.Merchant)
def generate_hash_id_and_sign_key(sender, instance, *args, **kwargs):
    if instance.is_new_record():
        instance.sign_key = secrets.token_hex(32)


@receiver(post_save, sender=models.Merchant)
def create_payment_methods_for_merhant(sender, instance, created, *args, **kwargs):
    if created:
        instance.create_payment_methods()


@receiver(pre_save, sender=models.Invoice)
def get_free_address(sender, instance, *args, **kwargs):
    if instance.is_new_record():
        query = {
            "status": "FREE",
            "chain_name": instance.payment_method.chain_name,
        }
        address = models.Address.objects.filter(**query).first()
        if address is None:
            address = models.Address.objects.create(**query)
        instance.address = address
        instance.address.reserve(
            timedelta_=instance.payment_method.expiration
        )
