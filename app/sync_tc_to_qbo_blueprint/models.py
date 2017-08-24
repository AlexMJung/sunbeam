import json
from app import app
from app.authorize_qbo_blueprint.models import qbo, AuthenticationTokens
import requests

class Parent(object):
    def __init__(self, tc_id=None, qbo_id=None, qbo_sync_token=None, first_name="", last_name="", email="", children=[]):
        self.tc_id = tc_id
        self.qbo_id = qbo_id
        self.qbo_sync_token = qbo_sync_token
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.children = children

    def to_qbo(self):
        return {
            "sparse": True,
            "Id": self.qbo_id,
            "SyncToken": self.qbo_sync_token,
            "GivenName": self.first_name,
            "FamilyName": self.last_name,
            "DisplayName": "{0} {1}".format(self.first_name, self.last_name),
            "PrimaryEmailAddr": {
                "Address": self.email
            },
            "Notes": json.dumps(
                {
                    "tc_id": self.tc_id,
                    "children": [{'name': c.name, 'program': c.program} for c in self.children]
                }
            )
        }

    @classmethod
    def from_qbo(cls, customer):
        try:
            d = json.loads(customer['Notes'])
            return Parent(tc_id=d['tc_id'], qbo_id=customer['Id'], qbo_sync_token=customer['SyncToken'], first_name=customer['GivenName'], last_name=customer['FamilyName'], email=customer['PrimaryEmailAddr']['Address'], children=[Child(name=c["name"], program=c["program"]) for c in d['children']])
        except Exception as e:
            return None

    @classmethod
    def parents_from_qbo(cls, company_id):
        qbo.authenticate_as(company_id)
        customers = qbo.get("https://quickbooks.api.intuit.com/v3/company/{0}/query?query=select%20%2A%20from%20customer&minorversion=4".format(company_id), headers={'Accept': 'application/json'}).data['QueryResponse']['Customer']
        return [p for p in [Parent.from_qbo(c) for c in customers] if p]

    @classmethod
    def parents_from_tc(cls, school_id):
        request_session = requests.session()
        request_session.headers.update({
            "X-TransparentClassroomToken": app.config['TRANSPARENT_CLASSROOM_API_TOKEN'],
            "X-TransparentClassroomSchoolId": "{0}".format(school_id),
            "Accept": "application/json"
        })

        users_response = request_session.get("{0}/api/v1/users.json".format(app.config["TRANSPARENT_CLASSROOM_BASE_URL"]))
        users = users_response.json()

        parents = []

        children_response = request_session.get("{0}/api/v1/children.json".format(app.config["TRANSPARENT_CLASSROOM_BASE_URL"]))
        for child in children_response.json():
            parent_ids = child.get('parent_ids', [])
            if len(parent_ids) > 0:
                for parent_id in parent_ids:
                    user = (u for u in users if u["id"] == parent_id).next()
                    parents.append(Parent(tc_id=parent_id, qbo_id=None, qbo_sync_token=None, first_name=user['first_name'], last_name=user['last_name'], email=user['email'], children=[Child(name="{0} {1}".format(child["first_name"], child["last_name"]), program="")]))

                    # XXX HANDLE MULTIPLE CHILD CASE!!!
                    # XXX INCLUDE PROGRAM !!!


        return parents;


class Child(object):
    def __init__(self, name="", program=""):
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
                tc_parent.qbo_sync_token = qbo_parent.qbo_sync_token
                tc_parent.qbo_id = qbo_parent.qbo_id
            app.logger.info("Syncing parent: {0} {1} ({2}) ({3})".format(tc_parent.first_name, tc_parent.last_name, tc_parent.tc_id, tc_parent.qbo_id))
            response = qbo.post("https://quickbooks.api.intuit.com/v3/company/{0}/customer".format(company_id), format='json', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot'}, data=tc_parent.to_qbo())
            if response.status != 200:
                raise LookupError, "create {0} {1} {2}".format(response.status, response.data, tc_parent)
