import unittest
import models
import flask
from app import app, db
import os
from app.authorize_qbo_blueprint.models import QBO, AuthenticationTokens

blueprint_name = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class TestCase(unittest.TestCase):
    def test_child_children_from_tc(self):
        assert models.Child.children_from_tc(278)

    def test_company(self):
        authentication_tokens = AuthenticationTokens.query.first()
        qbo_client = QBO(authentication_tokens.company_id).client(rate_limit=500)
        company = models.Company.company_from_qbo(authentication_tokens.company_id, qbo_client)
        assert company.name

    def test_school(self):
        assert models.School.schools_from_tc()

    def test_sync_children(self):
        models.sync_children()
