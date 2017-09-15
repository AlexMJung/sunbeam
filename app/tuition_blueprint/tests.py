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
    def setUp(self):
        self.company_id = AuthenticationTokens.query.first().company_id
        self.qbo_client = QBO(self.company_id).client()
        self.customer = models.Customer.customers_from_qbo(self.company_id, self.qbo_client)[0]
        self.item = next((i for i in models.Item.items_from_qbo(self.company_id, self.qbo_client) if i.price > 0), None)


    def test_with_bank_account(self):
        with app.test_request_context():
            # delete previously saved account
            qbo_bank_accounts = self.qbo_client.get("{0}/quickbooks/v4/customers/{1}/bank-accounts".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer.id), headers={'Accept': 'application/json'}).json()
            qbo_bank_account = next((b for b in qbo_bank_accounts if b['accountNumber'] == "xxxxxxxxxxxxx1111"), None)
            if qbo_bank_account:
                self.qbo_client.delete(
                    "{0}/quickbooks/v4/customers/{1}/bank-accounts/{2}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer.id, qbo_bank_account['id']),
                    headers={'Accept': 'application/json', 'Request-Id': str(uuid.uuid1())}
                )
            bank_account = models.BankAccount(customer=self.customer, name="Name", routing_number="121042882", account_number="11111111111111111", account_type="PERSONAL_CHECKING", phone="6128675309", qbo_client=self.qbo_client)
            bank_account.save()
            payment = models.Payment.payment_from_bank_account(self.company_id, bank_account, self.item.price, self.qbo_client)
            payment.update_status_from_qbo(self.qbo_client)
            sales_receipt = models.SalesReceipt(company_id=self.company_id, customer=self.customer, item=self.item, qbo_client=self.qbo_client)
            transaction_id = sales_receipt.save()
            sales_receipt.send()
            account = models.Account.deposit_account_from_qbo(self.company_id, self.qbo_client)
            models.Deposit(company_id=self.company_id, account=account, transaction_id=transaction_id, payment=payment, qbo_client=self.qbo_client).save()

    def test_with_credit_card(self):
        with app.test_request_context():
            # delete previously saved card
            qbo_cards = self.qbo_client.get("{0}/quickbooks/v4/customers/{1}/cards".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer.id), headers={'Accept': 'application/json'}).json()
            qbo_card = next((c for c in qbo_cards if c['number'] == "xxxxxxxxxxxx1111"), None)
            if qbo_card:
                self.qbo_client.delete(
                    "{0}/quickbooks/v4/customers/{1}/cards/{2}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer.id, qbo_card['id']),
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
            card = models.CreditCard(customer=self.customer, token=token, qbo_client=self.qbo_client)
            card.save()
            payment = models.Payment.payment_from_credit_card(self.company_id, card, self.item.price, self.qbo_client)
            cc_trans_id = payment.qbo_id
            payment.update_status_from_qbo(self.qbo_client)
            models.SalesReceipt(company_id=self.company_id, customer=self.customer, item=self.item, cc_trans_id=cc_trans_id, qbo_client=self.qbo_client).save()

    def test_declined_credit_card(self):
        with app.test_request_context():
            # delete previously saved card
            qbo_cards = self.qbo_client.get("{0}/quickbooks/v4/customers/{1}/cards".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer.id), headers={'Accept': 'application/json'}).json()
            qbo_card = next((c for c in qbo_cards if c['number'] == "xxxxxxxxxxxx1111"), None)
            if qbo_card:
                self.qbo_client.delete(
                    "{0}/quickbooks/v4/customers/{1}/cards/{2}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer.id, qbo_card['id']),
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
                        "name": "emulate=10401",
                        "cvc": "123",
                        "number": "4111111111111111"
                    }
                }
            )
            token = res.json()['value']
            card = models.CreditCard(customer=self.customer, token=token, qbo_client=self.qbo_client)
            card.save()
            payment = models.Payment.payment_from_credit_card(self.company_id, card, self.item.price, self.qbo_client)
            assert payment.status=="DECLINED"
