# Copyright (c) 2015 Presslabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from decimal import Decimal

from django.test import TestCase

from silver.models import DocumentEntry, Proforma, Invoice
from silver.tests.factories import (ProformaFactory, InvoiceFactory,
                                    DocumentEntryFactory)


class TestInvoice(TestCase):
    def test_pay_invoice_related_proforma_state_change_to_paid(self):
        proforma = ProformaFactory.create()
        proforma.issue()
        proforma.create_invoice()

        assert proforma.invoice.state == Invoice.STATES.ISSUED

        proforma.invoice.pay()
        proforma.invoice.save()

        assert proforma.invoice.state == Invoice.STATES.PAID
        assert proforma.state == Proforma.STATES.PAID

    def test_clone_invoice_into_draft(self):
        invoice = InvoiceFactory.create()
        invoice.issue()
        invoice.pay()
        invoice.save()

        entries = DocumentEntryFactory.create_batch(3)
        invoice.invoice_entries.add(*entries)

        clone = invoice.clone_into_draft()

        assert clone.state == Invoice.STATES.DRAFT
        assert clone.paid_date is None
        assert clone.issue_date is None
        assert clone.proforma is None
        assert (clone.series != invoice.series or
                clone.number != invoice.number)
        assert clone.sales_tax_percent == invoice.sales_tax_percent
        assert clone.sales_tax_name == invoice.sales_tax_name

        assert not clone.archived_customer
        assert not clone.archived_provider
        assert clone.customer == invoice.customer
        assert clone.provider == invoice.provider

        assert clone.currency == invoice.currency
        assert clone._last_state == clone.state
        assert clone.pk != invoice.pk
        assert clone.id != invoice.id
        assert not clone.pdf

        assert clone.invoice_entries.count() == 3
        assert invoice.invoice_entries.count() == 3

        entry_fields = [entry.name for entry in DocumentEntry._meta.get_fields()]
        for clone_entry, original_entry in zip(clone.invoice_entries.all(),
                                               invoice.invoice_entries.all()):
            for entry in entry_fields:
                if entry not in ('id', 'proforma', 'invoice'):
                    assert getattr(clone_entry, entry) == \
                        getattr(original_entry, entry)
        assert invoice.state == Invoice.STATES.PAID

    def test_cancel_issued_invoice_with_related_proforma(self):
        proforma = ProformaFactory.create()
        proforma.issue()

        if not proforma.invoice:
            proforma.create_invoice()

        proforma.invoice.cancel()
        proforma.invoice.save()

        assert proforma.invoice.state == proforma.state == Invoice.STATES.CANCELED

    def _get_decimal_places(self, number):
        return max(0, -number.as_tuple().exponent)

    def test_invoice_total_decimal_points(self):
        invoice_entries = DocumentEntryFactory.create_batch(3)
        invoice = InvoiceFactory.create(invoice_entries=invoice_entries)

        assert self._get_decimal_places(invoice.total) == 2

    def test_invoice_total_before_tax_decimal_places(self):
        invoice_entries = DocumentEntryFactory.create_batch(3)
        invoice = InvoiceFactory.create(invoice_entries=invoice_entries)

        invoice.sales_tax_percent = Decimal('20.00')

        assert self._get_decimal_places(invoice.total_before_tax) == 2

    def test_invoice_tax_value_decimal_places(self):
        invoice_entries = DocumentEntryFactory.create_batch(3)
        invoice = InvoiceFactory.create(invoice_entries=invoice_entries)

        invoice.sales_tax_percent = Decimal('20.00')

        assert self._get_decimal_places(invoice.tax_value) == 2

    def test_invoice_total_with_tax_integrity(self):
        invoice_entries = DocumentEntryFactory.create_batch(5)
        invoice = InvoiceFactory.create(invoice_entries=invoice_entries)

        invoice.sales_tax_percent = Decimal('20.00')

        assert invoice.total == invoice.total_before_tax + invoice.tax_value

    def test_draft_invoice_series_number(self):
        invoice = InvoiceFactory.create()
        invoice.number = None

        assert invoice.series_number == '%s-draft-id:%d' % (invoice.series,
                                                            invoice.pk)

        invoice.series = None

        assert invoice.series_number == 'draft-id:%d' % invoice.pk

    def test_issues_invoice_series_number(self):
        invoice = InvoiceFactory.create()

        assert invoice.series_number == '%s-%s' % (invoice.series,
                                                   invoice.number)
