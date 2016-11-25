from copy import deepcopy
from django.core.exceptions import ValidationError
import paypalrestsdk

from silver.models.payment_processors import GenericPaymentProcessor
from silver.models.payment_processors import TriggeredProcessorMixin
from silver.models.payment_processors import AutomaticProcessorMixin
from silver.models.transactions import Transaction
from silver.payment_processors.paypal.views import (PayPalTriggeredCreate,
                                                    PayPalAutomaticCreate)


class PayPalProcessor(GenericPaymentProcessor):
    name = None
    transaction_class = Transaction

    api = None

    def setup(self, data):
        self.api = paypalrestsdk.Api({
            'mode': data['mode'],
            'client_id': data['client_id'],
            'client_secret': data['client_secret']
        })

    def _get_data(self, payment_method):
        data = {
            'intent': 'sale',
            'redirect_urls': {
                'return_url': '',
                'cancel_url': ''
            },
            'payer': {
                'payment_method': 'paypal',
                'payer_info': {
                    'tax_id_type': payment_method.data['tax_id_type'],
                    'tax_id': payment_method.data['tax_id']
                }
            }
        }

        return data


class PayPalTriggered(PayPalProcessor, TriggeredProcessorMixin):
    name = 'PayPalTriggered'

    view_class = PayPalTriggeredCreate

    def refund_transaction(self, transaction, payment_method=None):
        pass

    def void_transaction(self, transaction, payment_method=None):
        pass

    def manage_transaction(self, transaction):
        payment_method = transaction.payment_method
        data = self._get_data(payment_method)
        data['redirect_urls']['return_url'] = ''.format(transaction.uuid)
        paypal_transaction = {
            'amount': {
                'total': transaction.amount,
                'currency': transaction.currency
            },
            'description': 'Presslabs services'
        }
        data['transactions'] = [paypal_transaction]
        payment = self.client.Payment(data, api=self.api)


class PayPalAutomatic(PayPalProcessor, AutomaticProcessorMixin):
    name = 'PayPalAutomatic'

    view_class = PayPalAutomaticCreate

    def setup(self, data):
        pass

    def setup_automated_transactions(self, customer):
        pass

    def charge_transaction(self, transaction, payment_method):
        pass

    def refund_transaction(self, transaction, payment_method=None):
        pass

    def void_transaction(self, transaction, payment_method=None):
        pass

    def manage_transaction(self, transaction):
        pass
