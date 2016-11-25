from django.conf.urls import url

from silver.payment_processors.paypal import views


urlpatterns = [
    url(r'^(?P<transaction_id>[0-9a-z-]+)/execute/?$',
        views.PayPalTriggeredExecute.as_view(), name='pay-pal-triggered-execute'),
    url(r'^(?P<transaction_id>[0-9a-z-]+)/cancel/?$',
        views.PayPalTriggeredCancel.as_view(), name='pay-pal-triggered-cancel'),
]
