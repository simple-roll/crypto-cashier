from core.models import Merchant


for merch in Merchant.objects.all():
    merch.create_payment_methods()
