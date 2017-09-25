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

    Database



## Global environment variables

    export MAIL_USERNAME="TBD"
    export MAIL_PASSWORD="TBD"


## Heroku environment variables

    heroku config:set APP_CONFIG_MODE=production


## Leaky abstractions / TODO

    Add flask cli command for copy generators/blueprint to app/whatever

    post_compile in the blueprints, composited to root

    requirements.txt in the blueprints, composited to root

    Automatically prefix table names in blueprints

    blueprint_name in tests feels leaky

    webpack config in the blueprints, composited to root

    nltk_data dir in root is leaky; should be beneath apply_blueprint (since used there)

    config is still a global namspace; isolate each blueprint's config?
