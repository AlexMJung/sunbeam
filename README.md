# Sunbeam

## Setup

    Clone repo
      git clone https://github.com/WildflowerSchools/sunbeam/

    Change to directory
      cd sunbeam

    Set up virtual env
      sudo pip install virtualenv
      virtualenv venv

    Activate virtual env
      . venv/bin/activate

    Install python packages
      pip install -r requirements.txt



## Heroku global environment variables

    heroku config:set APP_CONFIG_MODE=production
    heroku config:set MAIL_USERNAME=TBD
    heroku config:set MAIL_PASSWORD=TBD
    heroku config:set AWS_ACCESS_KEY_ID=TBD
    heroku config:set AWS_SECRET_ACCESS_KEY=TBD


## Leaky abstractions / TODO

    Add flask cli command for copy generators/blueprint to app/whatever

    post_compile in the blueprints, composited to root

    requirements.txt in the blueprints, composited to root

    Automatically prefix table names in blueprints

    blueprint_name in tests feels leaky

    webpack config in the blueprints, composited to root

    nltk_data dir in root is leaky; should be beneath apply_blueprint (since used there)

    config is still a global namspace; isolate each blueprint's config?
