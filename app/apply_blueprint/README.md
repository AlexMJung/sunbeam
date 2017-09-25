# Apply Blueprint

## Environment variables:

    export SURVEY_MONKEY_OAUTH_TOKEN="TBD"
    export APPLY_S3_BUCKET="TBD"
    export TRANSPARENT_CLASSROOM_API_TOKEN="TBD"
    export TRANSPARENT_CLASSROOM_API_TOKEN_SANDBOX="TBD"

## Heroku specific environment variables

    heroku config:set NLTK_DATA=/app/nltk_data

## Notes

    When embedding redirect_to_survey_monkey_with_guid links in website, be sure to
    include ?hub=lowercase_hub_name_from_config - e.g., https://wildflower-sunbeam.herokuapp.com/apply/redirect_to_survey_monkey_with_guid?hub=cambridge


### New school setup

    Create Google Account:
        Create Google apps account named "SCHOOL-NAME-appointments"
        In incognito window:
          Log in to new account

    Set up Calendly:
      Log in to Calendly as user with Admin or Owner privs
      Add new Google account as user

      In incognito window from above:
        Open Calendly invite email, click link, sign up/accept.
        Set timezone
        Update event types with appropriate days of week/times of days

    Set up DB:
      Update seeds

    Add teachers to Google Account:
      In incognito window (from above):
        Add/authorize forwarding addresses
        For each forwarding address:
          Create filter
            Forward email sent to the account's address to each forwarding address
        In calendar, share with forwarding address, with "make changes" permission

### Survey Monkey API call examples:

    curl -X GET -H "Authorization:bearer $SURVEY_MONKEY_OAUTH_TOKEN" -H "Content-Type:application/json" "https://api.surveymonkey.net/v3/surveys/"

    curl -X GET -H "Authorization:bearer $SURVEY_MONKEY_OAUTH_TOKEN" -H "Content-Type:application/json" "https://api.surveymonkey.net/v3/surveys/113377045/details"

    curl -X GET -H "Authorization:bearer $SURVEY_MONKEY_OAUTH_TOKEN" -H "Content-Type:application/json" "https://api.surveymonkey.net/v3/surveys/113377045/responses/bulk?sort_order=DESC"
