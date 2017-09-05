from app import app, db
import os
import uuid
from app.authorize_qbo_blueprint.models import qbo

tablename_prefix = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class Base(db.Model):
    __abstract__  = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class BankAccount(object):
    def __init__(self, customer_id=None, name=None, routing_number=None, account_number=None, account_type="PERSONAL_CHECKING", phone=None):
        self.customer_id = customer_id
        self.name = name
        self.routing_number = routing_number
        self.account_number = account_number
        self.account_type = account_type
        self.phone = phone

    def data(self):
        return {
            "name": self.name,
            "routingNumber": self.routing_number,
            "accountNumber": self.account_number,
            "accountType": self.account_type,
            "phone": self.phone
        }

    def save(self):
        response = qbo.post("{0}/quickbooks/v4/customers/{1}/bank-accounts".format(app.config["QBO_PAYMENTS_API_BASE_URL"], self.customer_id), format='json', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())}, data=self.data())
        if response.status != 201:
                raise LookupError, "save {0} {1} {2}".format(response.status, response.data, self)






# use payments api
# store CC
# store ACH for future use

# - connect to QB customer by using ID appropriately

# create accounting SalesReceipt
# - use CreditCardPayment

# - use automatic reconciliation for CC


# no related thing for echeck?


# https://developer.intuit.com/docs/0100_quickbooks_payments/0200_dev_guides/using_the_accounting_and_payments_apis_together

# send sales receipt to parent(s)

# specify where deposited to?
