from app import app, db
import os
import uuid
from app.authorize_qbo_blueprint.models import QBO, AuthenticationTokens
from decimal import Decimal
from datetime import datetime
from flask import render_template
from flask_mail import Mail, Message
import traceback
import time
from flask_marshmallow import Marshmallow

ma = Marshmallow(app)

class Repr(object):
    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )


class QBOPaymentsModel(Repr):
    def save(self):
        response = self.qbo_client.post(
            self.url,
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json=self.data()
        )

        if response.status_code != 201:
            return (False, response.text)
        return (True, response.json()['id'])

class BankAccount(QBOPaymentsModel):
    def __init__(self, id=None, customer=None, name=None, routing_number=None, account_number=None, account_type="PERSONAL_CHECKING", phone=None, qbo_client=None):
        self.id = id
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

    def __init__(self, id=None, customer=None, token=None, qbo_client=None):
        self.id = id
        self.customer = customer
        self.token = token
        self.url = "{0}/quickbooks/v4/customers/{1}/cards/createFromToken".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer.id)
        self.qbo_client = qbo_client

    def data(self):
        return {
            "value": self.token
        }

class QBOAccountingModel(Repr):
    def save(self):
        response = self.qbo_client.post(
            self.url,
            headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
            json=self.data()
        )
        if response.status_code != 200:
            return (False, response.text)
        return (True, response.json()[self.__class__.__name__]["Id"])

class InvoiceOrSalesReceipt(QBOAccountingModel):
    def __init__(self, id=None, recurring_payment=None, qbo_client=None):
        self.id = id
        self.recurring_payment = recurring_payment
        self.qbo_client = qbo_client
        self.url = None
        # not sure how to handle failure case here... will blow up and stop everything
        _, self.customer = Customer.customer_from_qbo(self.recurring_payment.company_id, self.recurring_payment.customer_id, self.qbo_client)
        # not sure how to handle failure case here... will blow up and stop everything
        _, self.item = Item.item_from_qbo(self.recurring_payment.company_id, self.recurring_payment.item_id, qbo_client)

    def data(self):
        data = {
            "Line": [{
                "Amount": str(self.recurring_payment.amount),
                "DetailType": "SalesItemLineDetail",
                "SalesItemLineDetail": {
                    "ItemRef": {
                        "value": str(self.item.id)
                    },
                    "UnitPrice": str(self.recurring_payment.amount),
                    "Qty": 1
                }
            }],
            "CustomerRef": {
                "value": str(self.recurring_payment.customer_id)
            }
        }
        if self.customer.email:
            data["BillEmail"] = {
                "Address": self.customer.email
            }
        return data

    def send(self):
        if self.customer.email:
            response = self.qbo_client.post(
                self.url + "/{0}/send".format(self.id),
                headers={'Accept': 'application/json', 'Content-Type': 'application/octet-stream', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())}
            )

            if response.status_code != 200:
                return (False, response.text)
            return (True, None)


class Invoice(InvoiceOrSalesReceipt):
    def __init__(self, id=None, recurring_payment=None, qbo_client=None):
        super(Invoice, self).__init__(id=id, recurring_payment=recurring_payment, qbo_client=qbo_client)
        self.url = "{0}/v3/company/{1}/invoice".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.recurring_payment.company_id)

class SalesReceipt(InvoiceOrSalesReceipt):
    def __init__(self, id=None, recurring_payment=None, payment=None, qbo_client=None):
        super(SalesReceipt, self).__init__(id=id, recurring_payment=recurring_payment, qbo_client=qbo_client)
        self.payment = payment
        self.url = "{0}/v3/company/{1}/salesreceipt".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], self.recurring_payment.company_id)

    def data(self):
        data = super(SalesReceipt, self).data()
        data["TxnSource"] = "IntuitPayment"
        # this <below/next>, according to the docs, sufficient to automatically create and reconcile the deposit
        if self.recurring_payment.credit_card_id:
            data['CreditCardPayment'] = {
                "CreditChargeInfo": {
                    "ProcessPayment": "true"
                },
                "CreditChargeResponse": {
                    "CCTransId": self.payment.qbo_id
                }
            }
        return data

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

class ORMBase(db.Model, Repr):
    __abstract__  = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

tablename_prefix = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class RecurringPayment(ORMBase):
    __tablename__ = "{0}_recurring_payment".format(tablename_prefix)
    company_id = db.Column(db.String(120))
    customer_id = db.Column(db.String(120))
    payments = db.relationship('Payment', backref='recurring_payment', cascade="all,delete")
    bank_account_id = db.Column(db.String(120))
    credit_card_id = db.Column(db.String(120))
    item_id = db.Column(db.String(120))
    amount = db.Column(db.Numeric(precision=8, scale=2))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    def make_payment(self, qbo_client):
        success, value = Item.item_from_qbo(self.company_id, self.item_id, qbo_client)
        if not success:
            message = {
                "subject": "Tuition utility - make_payment failed to retrieve item",
                "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                "recipients": ["dan.grigsby@wildflowerschools.org"],
                "body": "{0}\n\n{1}\n\n{2}".format(value, self)
            }
            return (False, value)
        item = value

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
            return (False, response.text)
        response_data = response.json()
        return (True, Payment(qbo_id=response_data['id'], status=response_data['status'], recurring_payment=self))

class Payment(ORMBase):
    __tablename__ = "{0}_payment".format(tablename_prefix)
    qbo_id = db.Column(db.String(120))
    status = db.Column(db.String(120))
    recurring_payment_id = db.Column(db.Integer, db.ForeignKey("{0}_recurring_payment.id".format(tablename_prefix)))

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
            return (False, response.text)
        return (True, response.json()['status'])

# this schema has to follow Payment, since Payment is a relationship of RecurringPayment
class RecurringPaymentSchema(ma.ModelSchema):
    class Meta:
        model = RecurringPayment
recurring_payment_schema = RecurringPaymentSchema(many=True)

class Company(Repr):
    def __init__(self, email=None):
        self.id = id
        self.email = email

    @classmethod
    def company_from_qbo(cls, company_id, qbo_client):
        response = qbo_client.get("{0}/v3/company/{1}/companyinfo/{1}?minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            return (False, reponse.text)
        data = response.json()["CompanyInfo"]
        return (True, Customer(email=data.get('Email', {"Address": None})['Address']))

# can use QBOAccountingModel as base class if ever need to save
class Customer(Repr):
    def __init__(self, id=None, email=None, name=None, recurring_payment=None):
        self.id = id
        self.email = email
        self.name = name
        self.recurring_payment = recurring_payment

    @classmethod
    def customers_from_qbo(cls, company_id, qbo_client):
        response = qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20customer%20maxresults%201000&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            return (False, response.text)
        return (True, [Customer(id=c['Id'], email=c.get('PrimaryEmailAddr', {"Address": None})['Address'], name=c['DisplayName'], recurring_payment=RecurringPayment.query.filter_by(company_id=c['Id']).first()) for c in response.json()['QueryResponse']['Customer']])

    @classmethod
    def customer_from_qbo(cls, company_id, customer_id, qbo_client):
        response = qbo_client.get("{0}/v3/company/{1}/customer/{2}?minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id, customer_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            return (False, response.text)
        response_data = response.json()["Customer"]
        return (True, Customer(id=response_data['Id'], email=response_data.get('PrimaryEmailAddr', {"Address": None})['Address'], name=response_data['DisplayName'], recurring_payment=RecurringPayment.query.filter_by(company_id=response_data['Id']).first()))

class CustomerSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'recurring_payment')
    recurring_payment = ma.Nested(RecurringPaymentSchema)
customers_schema = CustomerSchema(many=True)

# can use QBOAccountingModel as base class if ever need to save
class Item(Repr):
    def __init__(self, id=None, name=None, price=None):
        self.id = id
        self.name = name
        self.price = price

    @classmethod
    def items_from_qbo(cls, company_id, qbo_client):
        response = qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20item%20maxresults%201000&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            return (False, response.text)
        return (True, [Item(id=i['Id'], name=i['Name'], price=i['UnitPrice']) for i in response.json()['QueryResponse']['Item']])

    @classmethod
    def item_from_qbo(cls, company_id, item_id, qbo_client):
        response = qbo_client.get("{0}/v3/company/{1}/item/{2}".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id, item_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            return (False, response.text)
        qbo_item=response.json()['Item']
        return (True, Item(id=qbo_item['Id'], name=qbo_item['Name'], price=qbo_item['UnitPrice']))

class ItemSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'price')
items_schema = ItemSchema(many=True)

# can use QBOAccountingModel as base class if ever need to save
class Account(Repr):
    def __init__(self, id=None):
        self.id = id

    @classmethod
    def deposit_account_from_qbo(cls, company_id, qbo_client):
        # convention is that there is one checking account and it is where deposits are made - note set up implication
        response = qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20account%20where%20AccountSubType%3D%27Checking%27&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
        if response.status_code != 200:
            return (False, response.text)
        return (True, Account(id=response.json()['QueryResponse']['Account'][0]['Id']))

class MailWithLogging(Mail):
    def send(self, message):
        app.logger.critical(message)
        super(Mail, self).send(message)

# mail = MailWithLogging(app)
mail = Mail(app)

class Cron(object):
    @classmethod
    def run(cls):
        try:
            cls.update_payments()
            cls.make_payments()
        except Exception:
            mail.send(
                Message(
                    "Tuition Utility Cron.run - Error",
                    sender="Wildflower Schools <noreply@wildflowerschools.org>",
                    recipients=['dan.grigsby@wildflowerschools.org'],
                    body=traceback.format_exc()
                )
            )

    @classmethod
    def send_invoice(cls, company, recurring_payment, qbo_client):
        success, value = Customer.customer_from_qbo(recurring_payment.company_id, recurring_payment.customer_id, qbo_client)
        if not success:
            message = {
                "subject": "Tuition utility - send_invoice failed to fetch customer from qbo",
                "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                "recipients": ["dan.grigsby@wildflowerschools.org"],
                "body": "{0}\n\n{1}".format(value, recurring_payment)
            }
            mail.send(Message(**message))
            return
        customer = value

        invoice = Invoice(recurring_payment=recurring_payment, qbo_client=qbo_client)
        success, value = invoice.save()
        if not success:
            message = {
                "subject": "Tuition utility - send_invoice failed to save invoice",
                "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                "recipients": ["dan.grigsby@wildflowerschools.org"],
                "body": "{0}\n\n{1}".format(value, invoice)
            }
            mail.send(Message(**message))
            return

        if customer.email:
            message = {
                "subject": "Tuition payment for {0} declined".format(customer.name),
                "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                "recipients": [customer.email],
                "cc": [company.email],
                "bcc": ['dan.grigsby@wildflowerschools.org'],
                "html": render_template("failed_email.html", customer=customer)
            }
            mail.send(Message(**message))
            invoice.send()
        else:
            mail.send(
                Message(
                    "Tuition payment for {0} failed; no parent email on-file".format(customer.name),
                    sender="Wildflower Schools <noreply@wildflowerschools.org>",
                    recipients=[company.email],
                    bcc=['dan.grigsby@wildflowerschools.org'],
                    html=render_template("failed_no_email_email.html", customer=customer)
                )
            )

    @classmethod
    def update_payments(cls):
        for payment in Payment.query.filter_by(status="PENDING").all():
            authentication_token = AuthenticationTokens.query.filter_by(company_id = payment.recurring_payment.company_id).first()
            qbo_accounting_client = QBO(authentication_token.company_id).client(rate_limit=500)
            qbo_payments_client = QBO(authentication_token.company_id).client(rate_limit=40)
            success, value = Company.company_from_qbo(authentication_token.company_id, qbo_accounting_client)
            if not success:
                message = {
                    "subject": "Tuition utility - update_payments failed to fetch company from qbo",
                    "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                    "recipients": ["dan.grigsby@wildflowerschools.org"],
                    "body": "{0}\n\n{1}".format(value, authentication_token.company_id)
                }
                mail.send(Message(**message))
                continue
            company = value
            success, value = payment.update_status_from_qbo(qbo_payments_client)
            if not success:
                message = {
                    "subject": "Tuition utility - update_payments failed to update status from qbo",
                    "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                    "recipients": ["dan.grigsby@wildflowerschools.org"],
                    "body": "{0}\n\n{1}".format(value, payment)
                }
                mail.send(Message(**message))
                continue

            db.session.commit()
            if payment.status != "PENDING":
                if payment.status == "SUCCEEDED":
                    sales_receipt = models.SalesReceipt(recurring_payment=payment.recurring_payment, qbo_client=qbo_accounting_client)
                    success, value = sales_receipt.save()
                    if not success:
                        message = {
                            "subject": "Tuition utility - update_payments failed to save sales receipt",
                            "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                            "recipients": ["dan.grigsby@wildflowerschools.org"],
                            "body": "{0}\n\n{1}".format(value, sales_receipt)
                        }
                        mail.send(Message(**message))
                        continue
                    else:
                        transaction_id = value
                        success, value = sales_receipt.send()
                        if not success:
                            message = {
                                "subject": "Tuition utility - update_payments failed to send sales receipt",
                                "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                                "recipients": ["dan.grigsby@wildflowerschools.org"],
                                "body": "{0}\n\n{1}".format(value, sales_receipt)
                            }
                            mail.send(Message(**message))
                        success, value = Account.deposit_account_from_qbo(company.company_id, qbo_accounting_client)
                        if not success:
                            message = {
                                "subject": "Tuition utility - update_payments failed to retrieve deposit account",
                                "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                                "recipients": ["dan.grigsby@wildflowerschools.org"],
                                "body": "{0}\n\n{1}".format(value, company.company_id)
                            }
                            mail.send(Message(**message))
                        else:
                            deposit_account = value
                            deposit = Deposit(company_id=company.company_id, account=deposit_account, transaction_id=transaction_id, payment=payment, qbo_client=qbo_accounting_client)
                            success, value = deposit.save()
                            if not success:
                                message = {
                                    "subject": "Tuition utility - update_payments failed to save deposit",
                                    "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                                    "recipients": ["dan.grigsby@wildflowerschools.org"],
                                    "body": "{0}\n\n{1}".format(value, deposit)
                                }
                                mail.send(Message(**message))
                elif payment.status == "DECLINED":
                    Cron.send_invoice(company, payment.recurring_payment, qbo_accounting_client)

    @classmethod
    def make_payments(cls):
        now = datetime.now()
        for authentication_token in AuthenticationTokens.query.all():
            qbo_accounting_client = QBO(authentication_token.company_id).client(rate_limit=500)
            qbo_payments_client = QBO(authentication_token.company_id).client(rate_limit=40)
            success, value = Company.company_from_qbo(authentication_token.company_id, qbo_accounting_client)
            if not success:
                message = {
                    "subject": "Tuition utility - make_payments failed to fetch company from qbo",
                    "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                    "recipients": ["dan.grigsby@wildflowerschools.org"],
                    "body": "{0}\n\n{1}".format(value, authentication_token.company_id)
                }
                mail.send(Message(**message))
                continue

            company = value
            app.logger.info("Processing automatic tuition payments for {0}".format(authentication_token.company_id))
            for recurring_payment in RecurringPayment.query.filter_by(company_id=str(authentication_token.company_id)).all():
                if (recurring_payment.start_date < now and now <= recurring_payment.end_date):
                    # look for payment this month, skip if found
                    if not next((p for p in recurring_payment.payments if p.date_created.month() == now.month()), None):
                        app.logger.info("Processing recurring payment {0}".format(recurring_payment.id))
                        success, value = recurring_payment.make_payment(qbo_payments_client)
                        if not success:
                            message = {
                                "subject": "Tuition utility - make_payments failed to make payment",
                                "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                                "recipients": ["dan.grigsby@wildflowerschools.org"],
                                "body": "{0}\n\n{1}".format(value, recurring_payment)
                            }
                            mail.send(Message(**message))
                            continue
                        payment = value
                        db.session.add(payment)
                        db.session.commit()
                        if payment.status == "CAPTURED":
                            sales_receipt = SalesReceipt(recurring_payment=payment.recurring_payment, payment=payment, qbo_client=qbo_accounting_client)
                            success, value = sales_receipt.save()
                            if not success:
                                message = {
                                    "subject": "Tuition utility - make_payments failed to save sales receipt",
                                    "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                                    "recipients": ["dan.grigsby@wildflowerschools.org"],
                                    "body": "{0}\n\n{1}".format(value, sales_receipt)
                                }
                                mail.send(Message(**message))
                                continue
                            else:
                                success, value = sales_receipt.send()
                                if not success:
                                    message = {
                                        "subject": "Tuition utility - make_payments failed to send sales receipt",
                                        "sender": "Wildflower Schools <noreply@wildflowerschools.org>",
                                        "recipients": ["dan.grigsby@wildflowerschools.org"],
                                        "body": "{0}\n\n{1}".format(value, sales_receipt)
                                    }
                                    mail.send(Message(**message))
                                # no reason to do Deposit because QBO handles automatically for CC
                        elif payment.status == "DECLINED":
                            Cron.send_invoice(company, payment.recurring_payment, qbo_accounting_client)
