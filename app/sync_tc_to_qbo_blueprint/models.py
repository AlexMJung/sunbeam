import json
from app import app, db
from app.authorize_qbo_blueprint.models import QBO, AuthenticationTokens
import requests
import os

tablename_prefix = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class Company(object):
    def __init__(self, name=None):
        self.name = name

    @classmethod
    def company_from_qbo(cls, company_id, qbo_client):
        response = qbo_client.get("{0}/v3/company/{1}/companyinfo/{1}?minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'})
        return Company(name = response.json()["CompanyInfo"]["CompanyName"])

class School(object):
    def __init__(self, name=None, id=None):
        self.name = name
        self.id = id

    @classmethod
    def schools_from_tc(cls):
        request_session = requests.session()
        request_session.headers.update({
            "X-TransparentClassroomToken": app.config['TRANSPARENT_CLASSROOM_API_TOKEN'],
            "Accept": "application/json"
        })

        response = request_session.get("{0}/api/v1/schools.json".format(app.config["TRANSPARENT_CLASSROOM_BASE_URL"]))

        schools = []
        for o in response.json():
            if o['type'] == "School":
                schools.append(School(name=o['name'], id=o['id']))

        return schools


class Child(object):
    def __init__(self, tc_id=None, tc_program=None, qbo_id=None, qbo_sync_token=None, first_name="", last_name="", email=""):
        self.tc_id = tc_id
        self.tc_program = tc_program
        self.qbo_id = qbo_id
        self.qbo_sync_token = qbo_sync_token
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

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
                    "tc_program": self.tc_program
                }
            )
        }

    @classmethod
    def from_qbo(cls, customer):
        try:
            notes = json.loads(customer['Notes'])
            return Child(
                tc_id          = notes['tc_id'],
                tc_program     = notes["program"],
                qbo_id         = customer['Id'],
                qbo_sync_token = customer['SyncToken'],
                first_name     = customer['GivenName'],
                last_name      = customer['FamilyName'],
                email          = customer['PrimaryEmailAddr']['Address']
            )
        except Exception as e:
            return None

    @classmethod
    def children_from_qbo(cls, qbo_client, qbo_company_id):
        customers = qbo_client.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20customer&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], qbo_company_id), headers={'Accept': 'application/json'}).json()['QueryResponse'].get('Customer', [])
        return [child for child in [Child.from_qbo(customer) for customer in customers] if child]

    @classmethod
    def children_from_tc(cls, school_id):
        request_session = requests.session()
        request_session.headers.update({
            "X-TransparentClassroomToken": app.config['TRANSPARENT_CLASSROOM_API_TOKEN'],
            "X-TransparentClassroomSchoolId": "{0}".format(school_id),
            "Accept": "application/json"
        })

        users_response = request_session.get("{0}/api/v1/users.json".format(app.config["TRANSPARENT_CLASSROOM_BASE_URL"]))
        users = users_response.json()

        children = []
        children_response = request_session.get("{0}/api/v1/children.json".format(app.config["TRANSPARENT_CLASSROOM_BASE_URL"]))
        for child in children_response.json():
            email_addresses = []

            parent_ids = child.get('parent_ids', [])
            if len(parent_ids) > 0:
                for parent in (u for u in users if u['id'] in parent_ids):
                    if parent['email']:
                        email_addresses.append(parent['email'])

            email = ", ".join(email_addresses)

            child = Child(
                tc_id          = child['id'],
                tc_program     = child.get("program", ""),
                qbo_id         = None,
                qbo_sync_token = None,
                first_name     = child['first_name'],
                last_name      = child['last_name'],
                email          = email
            )
            children.append(child)
        return children;

def sync_children():
    app.logger.info("Syncing TC children to QBO customers")

    schools = School.schools_from_tc()

    for qbo_company_id in [a.company_id for a in AuthenticationTokens.query.all()]:
        qbo_client = QBO(qbo_company_id).client(rate_limit=500)

        company = Company.company_from_qbo(qbo_company_id, qbo_client)

        filtered_list = filter(lambda s: s.name == company.name, schools)

        if len(filtered_list) != 1:
            continue

        tc_school_id = filtered_list[0]

        qbo_children = Child.children_from_qbo(qbo_client, qbo_company_id)

        app.logger.info("Syncing: {0}".format(company.name))

        for tc_child in Child.children_from_tc(tc_school_id):
            qbo_child = next((c for c in qbo_children if c.tc_id == tc_child.tc_id), None)
            if qbo_child:
                tc_child.qbo_sync_token = qbo_child.qbo_sync_token
                tc_child.qbo_id = qbo_child.qbo_id
            app.logger.info("Syncing child: {0} {1} ({2}) ({3})".format(tc_child.first_name, tc_child.last_name, tc_child.tc_id, tc_child.qbo_id))
            response = qbo.post(
                "{0}/v3/company/{1}/customer".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], qbo_company_id),
                headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot'},
                json=tc_child.to_qbo()
            )
            if response.status_code != 200:
                raise LookupError, "create {0} {1} {2}".format(response.status_code, response.json(), tc_parent)
