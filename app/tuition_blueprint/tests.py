import unittest
import models
import flask
from app import app, db
import os
from app.authorize_qbo_blueprint.models import QBO, AuthenticationTokens
from random import randint
import uuid
import requests

blueprint_name = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.company_id = AuthenticationTokens.query.first().company_id
        cls.qbo_accounting_client = QBO(cls.company_id).client(rate_limit=499)
        cls.qbo_payments_client = QBO(cls.company_id).client(rate_limit=39)
        cls.customer = models.Customer.customers_from_qbo(cls.company_id, cls.qbo_accounting_client)[0]
        cls.item = next((i for i in models.Item.items_from_qbo(cls.company_id, cls.qbo_accounting_client) if i.price > 0), None)

        qbo_bank_accounts = cls.qbo_payments_client.get("{0}/quickbooks/v4/customers/{1}/bank-accounts".format(app.config["QBO_PAYMENTS_API_BASE_URL"], cls.customer.id), headers={'Accept': 'application/json'}).json()
        qbo_bank_account = next((b for b in qbo_bank_accounts if b['accountNumber'] == "xxxxxxxxxxxxx1111"), None)
        if qbo_bank_account:
            cls.qbo_payments_client.delete(
                "{0}/quickbooks/v4/customers/{1}/bank-accounts/{2}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], cls.customer.id, qbo_bank_account['id']),
                headers={'Accept': 'application/json', 'Request-Id': str(uuid.uuid1())}
            )
        cls.bank_account = models.BankAccount(customer=cls.customer, name="Name", routing_number="121042882", account_number="11111111111111111", account_type="PERSONAL_CHECKING", phone="6128675309", qbo_client=cls.qbo_payments_client)
        cls.bank_account.save()

        qbo_cards = cls.qbo_payments_client.get("{0}/quickbooks/v4/customers/{1}/cards".format(app.config["QBO_PAYMENTS_API_BASE_URL"], cls.customer.id), headers={'Accept': 'application/json'}).json()
        qbo_card = next((c for c in qbo_cards if c['number'] == "xxxxxxxxxxxx1111"), None)
        if qbo_card:
            cls.qbo_payments_client.delete(
                "{0}/quickbooks/v4/customers/{1}/cards/{2}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], cls.customer.id, qbo_card['id']),
                headers={'Accept': 'application/json', 'Request-Id': str(uuid.uuid1())}
            )
        # don't use qbo_client for this - this API does not - can not - have auth
        res = requests.post(
            "{0}/quickbooks/v4/payments/tokens".format(app.config["QBO_PAYMENTS_API_BASE_URL"]),
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json={
                "card": {
                    "expYear": "2020",
                    "expMonth": "02",
                    "address": {
                      "region": "CA",
                      "postalCode": "94086",
                      "streetAddress": "1130 Kifer Rd",
                      "country": "US",
                      "city": "Sunnyvale"
                    },
                    "name": "emulate=0",
                    "cvc": "123",
                    "number": "4111111111111111"
                }
            }
        )
        token = res.json()['value']
        cls.credit_card = models.CreditCard(customer=cls.customer, token=token, qbo_client=cls.qbo_payments_client)
        cls.credit_card.save()

    def test_recurring_payment_bank_account(self):
        with app.test_request_context():
            recurring_payment = models.RecurringPayment(
                company_id = TestCase.company_id,
                customer_id = TestCase.customer.id,
                bank_account_id = TestCase.bank_account.id,
                item_id = TestCase.item.id,
                amount = TestCase.item.price
            )
            db.session.add(recurring_payment)
            db.session.commit()

            payment = recurring_payment.make_payment(TestCase.qbo_payments_client)
            db.session.add(payment)
            db.session.commit()

            payment.update_status_from_qbo(TestCase.qbo_payments_client)

            sales_receipt = models.SalesReceipt(recurring_payment=payment.recurring_payment, qbo_client=TestCase.qbo_accounting_client)
            transaction_id = sales_receipt.save()
            sales_receipt.send()

            deposit_account = models.Account.deposit_account_from_qbo(TestCase.company_id, TestCase.qbo_accounting_client)
            models.Deposit(company_id=TestCase.company_id, account=deposit_account, transaction_id=transaction_id, payment=payment, qbo_client=TestCase.qbo_accounting_client).save()

            db.session.delete(recurring_payment)
            db.session.commit()

    def test_with_credit_card(self):
        with app.test_request_context():
            recurring_payment = models.RecurringPayment(
                company_id = TestCase.company_id,
                customer_id = TestCase.customer.id,
                credit_card_id = TestCase.credit_card.id,
                item_id = TestCase.item.id,
                amount = TestCase.item.price
            )
            db.session.add(recurring_payment)
            db.session.commit()

            payment = recurring_payment.make_payment(TestCase.qbo_payments_client)
            db.session.add(payment)
            db.session.commit()

            payment.update_status_from_qbo(TestCase.qbo_payments_client)

            db.session.delete(recurring_payment)
            db.session.commit()

    def test_delete(self):
        with app.test_request_context():
            recurring_payment = models.RecurringPayment(
                company_id = "123",
                customer_id = "123",
                bank_account_id = "123",
                item_id = "123",
                amount = 123.45
            )
            db.session.add(recurring_payment)
            db.session.commit()

            self.assertEqual(len(recurring_payment.payments), 0)

            payment = models.Payment(qbo_id="123", status="WHATEVER", recurring_payment=recurring_payment)

            db.session.add(payment)
            db.session.commit()

            assert payment.recurring_payment_id == recurring_payment.id
            self.assertEqual(len(recurring_payment.payments), 1)

            db.session.delete(recurring_payment)
            db.session.commit()

            self.assertEqual(models.Payment.query.get(payment.id), None)

    def test_cron(self):
        with app.test_request_context():
            pass
