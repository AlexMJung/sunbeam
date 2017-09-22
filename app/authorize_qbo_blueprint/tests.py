import unittest
import models
from app import app
import os
from datetime import datetime

blueprint_name = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class TestCase(unittest.TestCase):
    def test_rate_limit(self):
        with app.test_request_context():
            company_id = models.AuthenticationTokens.query.first().company_id
            qbo_client = models.QBO(company_id).client(rate_limit=10)
            then = datetime.now()
            qbo_client.get("{0}/v3/company/{1}/companyinfo/{1}?minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
            qbo_client.get("{0}/v3/company/{1}/companyinfo/{1}?minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
            seconds = (datetime.now() - then).total_seconds()
            assert seconds >= 6
