from app import app, db
import os
import uuid
from app.authorize_qbo_blueprint.models import QBO
from decimal import Decimal

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
    def __init__(self, id=None, company_id=None, customer=None, item=None, cc_trans_id=None, qbo_client=None):
        self.id = id
        self.company_id=company_id
        self.customer=customer
        self.item=item
        self.cc_trans_id=cc_trans_id
        self.qbo_client=qbo_client
        self.url = "{0}/v3/company/{1}/salesreceipt".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.company_id)

    def data(self):
        data = {
            "Line": [{
                "Amount": self.item.price,
                "DetailType": "SalesItemLineDetail",
                "SalesItemLineDetail": {
                    "ItemRef": {
                        "value": str(self.item.id)
                    },
                    "UnitPrice": self.item.price,
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
    def __init__(self, id=None, company_id=None, account=None, transaction_id=None, payment=None, qbo_client=None):
        self.id = id
        self.company_id = company_id
        self.account = account
        self.transaction_id = transaction_id
        self.payment = payment
        self.qbo_client = qbo_client
        self.url = "{0}/v3/company/{1}/deposit".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.company_id)

    def data(self):
        return {
            "DepositToAccountRef": {
                "value": self.account.id
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
            ],
            "PrivateNote": "ECheck {0}".format(self.payment.qbo_id)
        }

class Base(db.Model):
    __abstract__  = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

tablename_prefix = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class RecurringPayment(Base):
    __tablename__ = "{0}_recurring_payment".format(tablename_prefix)
    company_id = db.Column(db.String(120))
    customer_id = db.Column(db.String(120))
    payments = db.relationship('Payment', backref=db.backref('recurring_payment', cascade="all, delete-orphan", single_parent=True))
    bank_account_id = db.Column(db.String(120))
    credit_card_id = db.Column(db.String(120))
    item_id = db.Column(db.String(120))
    amount = db.Column(db.Numeric(precision=8, scale=2))
    end_date = db.Column(db.DateTime)

    def make_payment(self, qbo_client):
        item = Item.item_from_qbo(self.company_id, self.item_id, qbo_client)

        if self.bank_account_id:
            url = "{0}/quickbooks/v4/payments/echecks".format(app.config["QBO_PAYMENTS_API_BASE_URL"])
            data = {
                "paymentMode": "WEB",
                "bankAccountOnFile": str(self.bank_account_id)
            }
        elif self.credit_card_id:
            url = "{0}/quickbooks/v4/payments/charges".format(app.config["QBO_PAYMENTS_API_BASE_URL"])
            data = {
                "currency": "USD",
                "cardOnFile": str(self.credit_card_id)
            }

        if self.amount:
            data['amount'] = str(Decimal(self.amount).quantize(Decimal('.01'))) # https://stackoverflow.com/questions/3221654/specifying-number-of-decimal-places-in-python
        else:
            data['amount'] = str(Decimal(item.price).quantize(Decimal('.01'))) # https://stackoverflow.com/questions/3221654/specifying-number-of-decimal-places-in-python

        response = qbo_client.post(
            url,
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json=data
        )

        if response.status_code != 201:
                raise LookupError, "post {0} {1}".format(response.status_code, response.text)
        data = response.json()

        return Payment(qbo_id=data['id'], status=data['status'], recurring_payment=self)

class Payment(Base):
    __tablename__ = "{0}_payment".format(tablename_prefix)
    qbo_id = db.Column(db.String(120))
    status = db.Column(db.String(120))
    recurring_payment_id = db.Column(db.Integer, db.ForeignKey("{0}_recurring_payment.id".format(tablename_prefix)))
    db.relationship('RecurringPayment', backref='payment')

    def update_status_from_qbo(self, qbo_client):
        url = None
        if self.recurring_payment.credit_card_id:
            url = "{0}/quickbooks/v4/payments/charges/{1}".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.qbo_id)
        elif self.recurring_payment.bank_account_id:
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
    def __init__(self, id=None, email=None, name=None):
        self.id = id
        self.email = email
        self.name = name

    @classmethod
    def customers_from_qbo(cls, company_id, qbo_client):
        response = qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20customer%20maxresults%201000&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            raise LookupError, "query {0} {1}".format(response.status_code, response.text)
        return [Customer(id=c['Id'], email=c.get('PrimaryEmailAddr', {"Address": None})['Address'], name=c['DisplayName']) for c in response.json()['QueryResponse']['Customer']]

# can use QBOAccountingModel as base class if ever need to save
class Item(object):
    def __init__(self, id=None, name=None, price=None):
        self.id = id
        self.name = name
        self.price = price

    @classmethod
    def items_from_qbo(cls, company_id, qbo_client):
        response = qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20item%20maxresults%201000&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            raise LookupError, "query {0} {1}".format(response.status_code, response.text)
        return [Item(id=i['Id'], name=i['Name'], price=i['UnitPrice']) for i in response.json()['QueryResponse']['Item']]

    @classmethod
    def item_from_qbo(cls, company_id, item_id, qbo_client):
        response = qbo_client.get("{0}/v3/company/{1}/item/{2}".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id, item_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            raise LookupError, "get {0} {1}".format(response.status_code, response.text)
        qbo_item=response.json()['Item']
        return Item(id=qbo_item['Id'], name=qbo_item['Name'], price=qbo_item['UnitPrice'])


# can use QBOAccountingModel as base class if ever need to save
class Account(object):
    def __init__(self, id=None):
        self.id = id

    @classmethod
    def deposit_account_from_qbo(cls, company_id, qbo_client):
        # convention is that there is one checking account and it is where deposits are made - note set up implication
        response = qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20account%20where%20AccountSubType%3D%27Checking%27&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            raise LookupError, "query {0} {1}".format(response.status_code, response.text)
        return Account(id=response.json()['QueryResponse']['Account'][0]['Id'])



# update payment statuses, when echeck goes from X to Y make deposit
