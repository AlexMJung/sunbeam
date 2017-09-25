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
      psql -c "create database wf_development"
      psql -c "create database wf_test"

    Environment variables
      Find all the environment variables noted in the README.mds using
        grep "[[:space:]]\+export" -r app -h |sed -e "s/^[ \t]*//"

      Set to appropriate values


## Global environment variables

    export TEST_DATABASE_URL="postgresql://wf@localhost:5432/wf_test"
    export DEVELOPMENT_DATABASE_URL="postgresql://wf@localhost:5432/wf_development"
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
