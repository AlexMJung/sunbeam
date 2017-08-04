import json
from app import app
from app.authorize_qbo_blueprint.models import qbo, AuthenticationTokens

class Parent(object):
    def __init__(self, tc_id, qbo_id, first_name, last_name, email, children):
        self.tc_id = tc_id
        self.qbo_id = qbo_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.children = children

    def to_qbo(self):
        return json.dumps({
            "Customer": {
                "GivenName": self.first_name,
                "FamilyName": self.last_name,
                "Display Name": "{0} {1}".format(self.first_name, self.last_name),
                "PrimaryEmailAddr": {
                    "Address": self.email
                },
                "Notes": json.dumps({
                    "tc_id": self.tc_id,
                    "children": [{c.name, c.program} for c in self.children]
                })
            }
        })

    @classmethod
    def from_qbo(cls, customer):
        try:
            d = json.loads(customer['Notes'])
            return Parent(d['tc_id'], customer['Id'], customer['GivenName'], customer['FamilyName'], customer['PrimaryEmailAddr']['Address'], [Child(c.name, c.program) for c in d['children']])
        except Exception as e:
            return None

    @classmethod
    def parents_from_qbo(cls, company_id):
        qbo.authenticate_as(company_id)
        customers = qbo.get("https://quickbooks.api.intuit.com/v3/company/{0}/query?query=select%20%2A%20from%20customer&minorversion=4".format(company_id), headers={'Accept': 'application/json'}).data['QueryResponse']['Customer']
        return [p for p in [Parent.from_qbo(c) for c in customers] if p]

    @classmethod
    def parents_from_tc(cls):
        # TODO: use first parent for billing
        # TODO: use API
        return [Parent("1", None, "First", "Last", "foo@bar.com", [Child("Child", "Program")])]

class Child(object):
    def __init__(self, name, program):
        self.name = name
        self.program = program

def sync_parents():
    app.logger.info("Syncing TC parents to QBO customers")
    for company_id in [a.company_id for a in AuthenticationTokens.query.all()]:
        app.logger.info("Syncing QBO company id: {0}".format(company_id))
        qbo_parents = Parent.parents_from_qbo(company_id)
        for tc_parent in Parent.parents_from_tc():
            qbo_parent = next((p for p in qbo_parents if p.tc_id == tc_parent.tc_id), None)
            if qbo_parent:
                tc_parent.qbo_id = qbo_parent.qbo_id
            app.logger.info("Syncing parent: {0} {1} ({2}) ({4})".format(tc_parent.first_name, tc_parent.last_name, tc_parent.tc_id, tc_parent.qbo_id))
            response = qbo.post("https://quickbooks.api.intuit.com/v3/company/{0}/customer".format(company_id), format='json', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot'}, data=tc_parent.to_qbo())
            if response.status != 200:
                raise LookupError, "create {0} {1} {2}".format(response.status, response.data, tc_parent)
