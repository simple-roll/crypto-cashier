from django.urls import path, re_path
# from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = "core"
urlpatterns = [
    path(
        "create_invoice/", 
        # csrf_exempt(views.CreateInvoice.as_view()), 
        views.CreateInvoice.as_view(), 
        name="create_invoice"
    ),
    path(
        "invoice/<uuid:invoice_uuid>/",
        views.Invoice.as_view(),
        name="invoice"
    )
]
