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
                raise LookupError, "save {0} {1} {2}".format(response.status_code, response.text, self)
        self.id = response.json()['id']
        return self.id

class BankAccount(QBOPaymentsModel):
    def __init__(self, id=None, status=None, customer=None, name=None, routing_number=None, account_number=None, account_type="PERSONAL_CHECKING", phone=None, qbo_client=None):
        self.id = id
        self.status = status
        self.customer = customer
        self.name = name
        self.routing_number = routing_number
        self.account_number = account_number
        self.account_type = account_type
        self.phone = phone
        self.qbo_client = qbo_client
        self.url = "{0}/quickbooks/v4/customers/{1}/bank-accounts".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer.id)

    @classmethod
    def bank_account_for(cls, qbo_client, customer, bank_account_id):
        return BankAccount(id=bank_account_id, customer=customer, qbo_client=qbo_client)

    def data(self):
        return {
            "name": self.name,
            "routingNumber": self.routing_number,
            "accountNumber": self.account_number,
            "accountType": self.account_type,
            "phone": self.phone
        }

class CreditCard(QBOPaymentsModel):
    # We only create cards via tokens.  This allows us to use a client-side form to interact with
    # Intuit's API to store the CC, allowing us to avoid PCI compliance hassles.

    def __init__(self, id=None, status=None, customer=None, token=None, qbo_client=None):
        self.id = id,
        self.status = status,
        self.customer = customer
        self.token = token
        self.url = "{0}/quickbooks/v4/customers/{1}/cards/createFromToken".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer.id)
        self.qbo_client = qbo_client

    def data(self):
        return {
            "value": self.token
        }

class QBOAccountingModel(object):
    def save(self):
        response = self.qbo_client.post(
            self.url,
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json=self.data()
        )
        if response.status_code != 200:
                raise LookupError, "save {0} {1} {2}".format(response.status_code, response.text, self)
        self.id = response.json()[self.__class__.__name__]["Id"]
        return self.id

class SalesReceipt(QBOAccountingModel):
    def __init__(self, id=None, company_id=None, customer=None, item_id=None, amount=None, cc_trans_id=None, qbo_client=None):
        self.id = id
        self.company_id=company_id
        self.customer=customer
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
                "value": str(self.customer.id)
            },
            "TxnSource": "IntuitPayment"
        }

        if self.customer.email:
            data["BillEmail"] = {
                "Address": self.customer.email
            }

        # this is, according to the docs, sufficient to automatically create and reconcile the deposit
        if self.cc_trans_id:
            data['CreditCardPayment'] = {
                "CreditChargeInfo": {
                    "ProcessPayment": "true"
                },
                "CreditChargeResponse": {
                    "CCTransId": self.cc_trans_id
                }
            }

        return data

    def send(self):
        response = self.qbo_client.post(
            "{0}/v3/company/{1}/salesreceipt/{2}/send".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.company_id, self.id),
            headers={'Accept': 'application/json', 'Content-Type': 'application/octet-stream', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())}
        )
        if response.status_code != 200:
            raise LookupError, "save {0} {1} {2}".format(response.status_code, response.text, self)

class Deposit(QBOAccountingModel):
    def __init__(self, id=None, company_id=None, account_id=None, transaction_id=None, qbo_client=None):
        self.id = id
        self.company_id = company_id
        self.account_id = account_id
        self.transaction_id = transaction_id
        self.qbo_client = qbo_client
        self.url = "{0}/v3/company/{1}/deposit".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.company_id)

    def data(self):
        return {
            "DepositToAccountRef": {
                "value": self.account_id
            },
            "Line":[
                {
                    "LinkedTxn":[
                        {
                            "TxnId": self.transaction_id,
                            "TxnLineId": "0",
                            "TxnType": "SalesReceipt"
                        }
                    ]
                }
            ]
        }

class Base(db.Model):
    __abstract__  = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

tablename_prefix = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class Payment(Base):
    __tablename__ = "{0}_school".format(tablename_prefix)
    qbo_id = db.Column(db.String(120))
    method = db.Column(db.String(120))
    status = db.Column(db.String(120))

    @classmethod
    def payment_from_bank_account(cls, bank_account, amount, qbo_client):
        response = qbo_client.post(
            "{0}/quickbooks/v4/payments/echecks".format(app.config["QBO_PAYMENTS_API_BASE_URL"]),
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json={
                "amount": str(amount),
                "paymentMode": "WEB",
                "bankAccountOnFile": str(bank_account.id)
            }
        )
        if response.status_code != 201:
                raise LookupError, "post {0} {1}".format(response.status_code, response.text)
        data = response.json()
        return Payment(
            method="BankAccount",
            qbo_id=data['id'],
            status=data['status']
        )

    @classmethod
    def payment_from_credit_card(cls, credit_card, amount, qbo_client):
        response = qbo_client.post(
            "{0}/quickbooks/v4/payments/charges".format(app.config["QBO_PAYMENTS_API_BASE_URL"]),
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json={
                "amount": str(amount),
                "currency": "USD",
                "cardOnFile": str(credit_card.id)
            }
        )
        if response.status_code != 201:
                raise LookupError, "post {0} {1}".format(response.status_code, response.text)
        data = response.json()
        return Payment(
            method="CreditCard",
            qbo_id=data['id'],
            status=data['status']
        )

    def update_status_from_qbo(self, qbo_client):
        if self.method == "CreditCard":
            url = "{0}/quickbooks/v4/payments/charges/{1}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.qbo_id)
        elif self.method == "BankAccount":
            url = "{0}/quickbooks/v4/payments/echecks/{1}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.qbo_id)
        response = qbo_client.get(
            url,
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
        )
        if response.status_code != 200:
                raise LookupError, "save {0} {1} {2}".format(response.status_code, response.text, self)
        self.status = response.json()['status']
        return self.status

# can use QBOAccountingModel as base class if ever need to save
class Customer(object):
    def __init__(self, id=None, email=None):
        self.id = id
        self.email = email

    @classmethod
    def customers_from_qbo(cls, company_id, qbo_client):
        response = qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20customer%20maxresults%201000&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            raise LookupError, "query {0} {1}".format(response.status_code, response.text)
        return [Customer(id=c['Id'], email=c.get('PrimaryEmailAddr', {"Address": None})['Address']) for c in response.json()['QueryResponse']['Customer']]



# switch from customer_id to Customer object

# make deposit show/link/note echeck payment XXX HERE !!!

# do work to get list of services, accounts, etc. that will be necessary for automation
#  may not need to save many - all of these...

# use API to get all services - or things they sell - and use that to let them select which thing to sell for full day, half day, etc
