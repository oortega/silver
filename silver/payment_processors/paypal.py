from silver.models.payment_processors import (GenericPaymentProcessor, ManualProcessorMixin,
                                              TriggeredProcessorMixin, AutomaticProcessorMixin)


class PayPalTriggered(GenericPaymentProcessor, TriggeredProcessorMixin):
    name = 'PayPalTriggered'

    def setup(self, data):
        pass

    def charge_payment(self, payment, payment_method):
        pass

    def refund_payment(self, payment, payment_method=None):
        pass

    def void_payment(self, payment, payment_method=None):
        pass

    def manage_payment(self, payment):
        pass


class PayPalAutomatic(GenericPaymentProcessor, AutomaticProcessorMixin):
    name = 'PayPalAutomatic'

    def setup(self, data):
        pass

    def setup_automated_payments(self, customer):
        pass

    def charge_payment(self, payment, payment_method):
        pass

    def refund_payment(self, payment, payment_method=None):
        pass

    def void_payment(self, payment, payment_method=None):
        pass

    def manage_payment(self, payment):
        pass
