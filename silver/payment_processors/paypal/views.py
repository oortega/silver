from rest_framework.generics import (APIView, CreateAPIView)


class PayPalTriggeredCreate(CreateAPIView):
    def handle_transaction_request(self, request, transaction):
        payment_processor = transaction.payment_method.payment_processor
        payment_processor.manage_transaction(transaction)


class PayPalTriggeredExecute(APIView):
    pass


class PayPalTriggeredCancel(APIView):
    pass


class PayPalAutomaticCreate(CreateAPIView):
    def handle_transaction_request(self, request, transaction):
        pass
