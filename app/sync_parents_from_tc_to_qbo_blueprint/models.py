import json
from app.authorize_qbo_blueprint.models import qbo, AuthenticationTokens

class Parent(Object):
    def __init__(self, tc_id, first_name, last_name, email, children):
        self.tc_id = tc_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.children = children

    def to_qbo_json(self):
        return json.dumps({
            Customer": {
                "GivenName": self.first_name,
                "FamilyName": self.last_name,
                "Display Name": "{0} {1}".format(self.first_name, self.last_name),
                "PrimaryEmailAddr": {
                    "Address": self.email
                },
                "Notes": json.dumps({
                    "tc_id": self.tc_id
                    "children": [{c.name, c.program} for c in self.children]
                })
            }
        })

    @classmethod
    def from_qbo(customer):
        d = json.loads(customer['Notes'])
        return Parent(d['tc_id'], customer['GivenName'], customer['FamilyName'], customer['PrimaryEmailAddr']['Address'], [Child(c.name, c.program) for c in d['children']])

    @classmethod
    def parents_from_qbo(company_id):
        qbo.authenticate_as(company_id)
        return [Parent.from_qbo(c) for c in qbo.get("https://quickbooks.api.intuit.com/v3/company/{0}/query?query=select%20%2A%20from%20customer&minorversion=4".format(company_id), headers={'Accept': 'application/json'}).data['QueryResponse']['Customer']]

    @classmethod
    def parents_from_tc():
        # TODO: use first parent for billing
        # TODO: use API
        return [Parent("1", "First", "Last", "foo@bar.com", [Child("Child", "Program")])]

class Child(Object):
    def __init__(self, name, program):
        self.name = name
        self.program = program

def sync():
    for company_id in [a.company_id for a in AuthenticationTokens.query.all()]:
        qbo_parents = Parent.parents_from_qbo(company_id)
        for tc_parent in Parent.parents_from_tc():
            if any(qbo_parent.tc_id == tc_parent.tc_id for qbo_parent in qbp_parents): # update in qbo
                pass
            else: # create in qbo
                pass
