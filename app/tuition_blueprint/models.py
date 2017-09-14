from app import app, db
import os
import uuid
from app.authorize_qbo_blueprint.models import QBO

class QBOPaymentsModel(object):
    def save(self):
        response = self.qbo_client.post(
            self.url,
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json=self.data()
        )
        if response.status_code != 201:
                raise LookupError, "save {0} {1} {2}".format(response.status_code, response.json(), self)
        self.id = response.json()['id']

class BankAccount(QBOPaymentsModel):
    def __init__(self, id=None, customer_id=None, name=None, routing_number=None, account_number=None, account_type="PERSONAL_CHECKING", phone=None, qbo_client=None):
        self.id = id
        self.customer_id = customer_id
        self.name = name
        self.routing_number = routing_number
        self.account_number = account_number
        self.account_type = account_type
        self.phone = phone
        self.qbo_client = qbo_client
        self.url = "{0}/quickbooks/v4/customers/{1}/bank-accounts".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer_id)

    @classmethod
    def bank_account_for(cls, qbo_client, customer_id, bank_account_id):
        return BankAccount(id=bank_account_id, customer_id=customer_id, qbo_client=qbo_client)

    def data(self):
        return {
            "name": self.name,
            "routingNumber": self.routing_number,
            "accountNumber": self.account_number,
            "accountType": self.account_type,
            "phone": self.phone
        }

    def debit(self, amount):
        response = self.qbo_client.post(
            "{0}/quickbooks/v4/payments/echecks".format(app.config["QBO_PAYMENTS_API_BASE_URL"]),
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json={
                "amount": str(amount),
                "paymentMode": "WEB",
                "bankAccountOnFile": str(self.id)
            }
        )
        if response.status_code != 201:
                raise LookupError, "save {0} {1} {2}".format(response.status_code, response.json(), self)

class CreditCard(QBOPaymentsModel):
    # We only create cards via tokens.  This allows us to use a client-side form to interact with
    # Intuit's API to store the CC, allowing us to avoid PCI compliance hassles.

    def __init__(self, id=None, customer_id=None, token=None, qbo_client=None):
        self.customer_id = customer_id
        self.token = token
        self.url = "{0}/quickbooks/v4/customers/{1}/cards/createFromToken".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer_id)
        self.qbo_client = qbo_client

    def data(self):
        return {
            "value": self.token
        }

    def charge(self, amount):
        response = self.qbo_client.post(
            "{0}/quickbooks/v4/payments/charges".format(app.config["QBO_PAYMENTS_API_BASE_URL"]),
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json={
                "amount": str(amount),
                "currency": "USD",
                "cardOnFile": str(self.id)
            }
        )
        if response.status_code != 201:
                raise LookupError, "save {0} {1} {2}".format(response.status_code, response.json(), self)
        return response.json()['id']

class QBOAccountingModel(object):
    def save(self):
        response = self.qbo_client.post(
            self.url,
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json=self.data()
        )
        if response.status_code != 200:
                raise LookupError, "save {0} {1} {2}".format(response.status_code, response.json(), self)
        self.id = response.json()[self.__class__.__name__]["Id"]


class SalesReceipt(QBOAccountingModel):
    def __init__(self, id=None, company_id=None, customer_id=None, item_id=None, amount=None, cc_trans_id=None, qbo_client=None):
        self.id = id
        self.company_id=company_id
        self.customer_id=customer_id
        self.item_id=item_id
        self.amount=amount
        self.cc_trans_id=cc_trans_id
        self.qbo_client=qbo_client
        self.url = "{0}/v3/company/{1}/salesreceipt".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.company_id)

    def data(self):
        data = {
            "Line": [{
                "Amount": self.amount,
                "DetailType": "SalesItemLineDetail",
                "SalesItemLineDetail": {
                    "ItemRef": {
                        "value": str(self.item_id)
                    },
                    "UnitPrice": self.amount,
                    "Qty": 1
                }
            }],
            "CustomerRef": {
                "value": str(self.customer_id)
            },
            "TxnSource": "IntuitPayment"
        }

        # this is, according to the docs, sufficient to automatically create and reconcile the deposit
        if (self.cc_trans_id):
            data['CreditCardPayment'] = {
                "CreditChargeInfo": {
                    "ProcessPayment": "true"
                },
                "CreditChargeResponse": {
                    "CCTransId": self.cc_trans_id
                }
            }
        return data





# handle failed CC (instant)
# handle failed echeck (delayed)


# use API to get all services - or things they sell - and use that to let them select which thing to sell for full day, half day, etc

# - connect to QB customer by using ID appropriately




# create accounting SalesReceipt
# - use CreditCardPayment

# - use automatic reconciliation for CC
# no related thing for echeck?


# https://developer.intuit.com/docs/0100_quickbooks_payments/0200_dev_guides/using_the_accounting_and_payments_apis_together

# send sales receipt to parent(s)

# specify where deposited to?

# tablename_prefix = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]
#
# class Base(db.Model):
#     __abstract__  = True
#     id = db.Column(db.Integer, primary_key=True)
#     date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
#     date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
