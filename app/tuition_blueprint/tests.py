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
        self.customer_id = self.qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20customer&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.company_id), headers={'Accept': 'application/json'}).json()['QueryResponse']['Customer'][0]['Id']

    def test_with_bank_account(self):
        with app.test_request_context():
            # delete previously saved account
            qbo_bank_accounts = self.qbo_client.get("{0}/quickbooks/v4/customers/{1}/bank-accounts".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer_id), headers={'Accept': 'application/json'}).json()
            qbo_bank_account = next((b for b in qbo_bank_accounts if b['accountNumber'] == "xxxxxxxxxxxxx1111"), None)
            if qbo_bank_account:
                self.qbo_client.delete(
                    "{0}/quickbooks/v4/customers/{1}/bank-accounts/{2}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer_id, qbo_bank_account['id']),
                    headers={'Accept': 'application/json', 'Request-Id': str(uuid.uuid1())}
                )
            bank_account = models.BankAccount(customer_id=self.customer_id, name="Name", routing_number="121042882", account_number="11111111111111111", account_type="PERSONAL_CHECKING", phone="6128675309", qbo_client=self.qbo_client)
            bank_account.save()
            amount = 1928.37
            payment = models.Payment.payment_from_bank_account(bank_account, amount, self.qbo_client)
            payment.update_status_from_qbo(self.qbo_client)
            item_id = self.qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20item&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.company_id), headers={'Accept': 'application/json'}).json()['QueryResponse']['Item'][0]['Id']
            sales_receipt = models.SalesReceipt(company_id=self.company_id, customer_id=self.customer_id, item_id=item_id, amount=amount, qbo_client=self.qbo_client)
            transaction_id = sales_receipt.save()
            # sales_receipt.send() -> this is generating a 500 from QB; I /think/ it's a sandbox issue
            account_id = self.qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20account%20where%20AccountSubType%3D%27Checking%27&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.company_id), headers={'Accept': 'application/json'}).json()['QueryResponse']['Account'][0]['Id']
            models.Deposit(company_id=self.company_id, account_id=account_id, transaction_id=transaction_id, qbo_client=self.qbo_client).save()

    def test_with_credit_card(self):
        with app.test_request_context():
            # delete previously saved card
            qbo_cards = self.qbo_client.get("{0}/quickbooks/v4/customers/{1}/cards".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer_id), headers={'Accept': 'application/json'}).json()
            qbo_card = next((c for c in qbo_cards if c['number'] == "xxxxxxxxxxxx1111"), None)
            if qbo_card:
                self.qbo_client.delete(
                    "{0}/quickbooks/v4/customers/{1}/cards/{2}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer_id, qbo_card['id']),
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
            card = models.CreditCard(customer_id=self.customer_id, token=token, qbo_client=self.qbo_client)
            card.save()
            amount = 345.67
            payment = models.Payment.payment_from_credit_card(card, amount, self.qbo_client)
            cc_trans_id = payment.qbo_id
            payment.update_status_from_qbo(self.qbo_client)
            item_id = self.qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20item&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.company_id), headers={'Accept': 'application/json'}).json()['QueryResponse']['Item'][0]['Id']
            models.SalesReceipt(company_id=self.company_id, customer_id=self.customer_id, item_id=item_id, amount=amount, cc_trans_id=cc_trans_id, qbo_client=self.qbo_client).save()

    def test_declined_credit_card(self):
        with app.test_request_context():
            # delete previously saved card
            qbo_cards = self.qbo_client.get("{0}/quickbooks/v4/customers/{1}/cards".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer_id), headers={'Accept': 'application/json'}).json()
            qbo_card = next((c for c in qbo_cards if c['number'] == "xxxxxxxxxxxx1111"), None)
            if qbo_card:
                self.qbo_client.delete(
                    "{0}/quickbooks/v4/customers/{1}/cards/{2}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer_id, qbo_card['id']),
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
            card = models.CreditCard(customer_id=self.customer_id, token=token, qbo_client=self.qbo_client)
            card.save()
            amount = 345.67
            payment = models.Payment.payment_from_credit_card(card, amount, self.qbo_client)
            assert payment.status=="DECLINED"
