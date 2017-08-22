from app import app, db
import os
import sqlalchemy.orm
import urllib
import requests
import time
from flask_marshmallow import Marshmallow

tablename_prefix = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]
ma = Marshmallow(app)

class Base(db.Model):
    __abstract__  = True
    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

def slack_api(method, arguments = {}):
    url = "https://slack.com/api/{0}?token={1}&{2}".format(method, app.config['SLACK_API_TOKEN'], urllib.urlencode(arguments))
    while True:
        response = requests.get(url)
        if response.status_code == 429:
            print "rate limited; sleeping for {0} seconds".format(response.headers[Retry-After])
            time.sleep(float(response.headers[Retry-After]))
        else:
            # print response.text
            return response.json()

class PublicProfile(Base):
    __tablename__ = "{0}_public_profile".format(tablename_prefix)
    slack_id      = db.Column(db.String(120))
    name          = db.Column(db.String(120))
    role          = db.Column(db.String(120))
    img_url       = db.Column(db.String(256))
    bio           = db.Column(db.String(256))

    @classmethod
    def create_for(cls, slack_id):
        slack_profile = slack_api("users.profile.get", {"user": slack_id})["profile"]
        if slack_profile.get("fields") and len(slack_profile.get("fields").get("Xf4ZLD1W8Z",{}).get("value", "")) > 0:
            return PublicProfile(
                slack_id  = slack_id,
                name      = slack_profile.get("real_name"),
                role      = slack_profile.get("title"),
                img_url   = slack_profile.get("image_512"),
                bio       = slack_profile.get("fields").get("Xf4ZLD1W8Z").get("value")
            )
        return None

    @classmethod
    def seed_from_slack(cls):
        user_list = slack_api("users.list")["members"]
        for user in user_list:
            if not user['deleted']:
                profile = PublicProfile.create_for(user['id'])
                if profile:
                    db.session.add(profile)
        db.session.commit()

    # update isn't exactly correct; can also include delete and create; handles case where was public now private
    @classmethod
    def update_profile_from_slack_event(cls, user):
        db.session.query(PublicProfile).filter_by(slack_id=user['id']).delete()
        if not user['deleted']: # update
            new_profile = PublicProfile.create_for(user['id'])
            if new_profile:
                db.session.add(new_profile)
        db.session.commit()

class PublicProfileSchema(ma.ModelSchema):
    class Meta:
        model = PublicProfile
