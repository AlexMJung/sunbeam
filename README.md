## Heroku global environment variables
Global Heroku config/env vars:

heroku config:set APP_CONFIG_MODE=production
heroku config:set MAIL_USERNAME=TBD
heroku config:set MAIL_PASSWORD=TBD
heroku config:set AWS_ACCESS_KEY_ID=TBD
heroku config:set AWS_SECRET_ACCESS_KEY=TBD


TODO:
  set tablename_prefix and blueprint_name in __init


  Add flask cli command to create scaffolding blueprint w. empty req'd files
  post_compile in the blueprints, composited to root
  requirements.txt in the blueprints, composited to root


  Automatically prefix table names in blueprints (flask_sqlalchemy is causing problems)
  blueprint_name in tests feels leaky
  webpack config in the blueprints, composited to root
  nltk_data dir in root is leaky
  Config is still a global namspace; isolate each blueprint's config
  make 500 global and apply everywhere -  maybe copy template when create, update email
