import json
from app import app, db
from app.authorize_qbo_blueprint.models import QBO, AuthenticationTokens
import requests
import os

tablename_prefix = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class Base(db.Model):
    __abstract__  = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class School(Base):
    __tablename__ = "{0}_school".format(tablename_prefix)
    tc_school_id = db.Column(db.Integer)
    qbo_company_id = db.Column(db.BigInteger)

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
    def children_from_qbo(cls, qbo):
        customers = qbo.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20customer&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'}).data['QueryResponse'].get('Customer', [])
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
            parent_ids = child.get('parent_ids', [])
            if len(parent_ids) > 0:
                parents = (u for u in users if u['id'] in parent_ids)
                child = Child(
                    tc_id          = child['id'],
                    tc_program     = child.get("program", ""),
                    qbo_id         = None,
                    qbo_sync_token = None,
                    first_name     = child['first_name'],
                    last_name      = child['last_name'],
                    email          = ", ".join([p['email'] for p in parents])
                )
                print child
                children.append(child)
        return children;

def sync_children():
    app.logger.info("Syncing TC children to QBO customers")
    for qbo_company_id in [a.company_id for a in AuthenticationTokens.query.all()]:
        app.logger.info("Syncing QBO company id: {0}".format(qbo_company_id))
        qbo = QBO(qbo_company_id).client(rate_limit=500)
        qbo_children = Child.children_from_qbo(qbo)
        for tc_child in Child.children_from_tc(School.query.filter_by(qbo_company_id=qbo_company_id).first().tc_school_id):
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
