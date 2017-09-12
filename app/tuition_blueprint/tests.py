import unittest
import models
import flask
from app import app, db
import os
from app.authorize_qbo_blueprint.models import QBO, AuthenticationTokens
from random import randint

blueprint_name = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class TestCase(unittest.TestCase):
    def test_save_bank_account(self):
        with app.test_request_context():
            company_id = AuthenticationTokens.query.first().company_id
            qbo = QBO(company_id).client()
            customer_id = qbo.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20customer&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'}).json()['QueryResponse']['Customer'][0]['Id']
            models.BankAccount(customer_id=customer_id, name="Name", routing_number="121042882", account_number=str(randint(1000, 99999999999999999)), account_type="PERSONAL_CHECKING", phone="6128675309").save(qbo)
