import os

SURVEY_MONKEY_OAUTH_TOKEN=os.environ['SURVEY_MONKEY_OAUTH_TOKEN']
TRANSPARENT_CLASSROOM_API_TOKEN=os.environ['TRANSPARENT_CLASSROOM_API_TOKEN']

SURVEY_MONKEY_SURVEY_ID='111419034'
SURVEY_MONKEY_COLLECTOR_ID='FQDVNM3'

ANSWER_KEY = {
    'PARENTS': [
        {
            'FIRST_NAME': {'SURVEY_MONKEY': '69078793', 'TRANSPARENT_CLASSROOM': 'first_parent_name.first'},
            'LAST_NAME': {'SURVEY_MONKEY': '77425064', 'TRANSPARENT_CLASSROOM': 'first_parent_name.last'} ,
            'EMAIL': {'SURVEY_MONKEY': '69078871', 'TRANSPARENT_CLASSROOM': 'first_parent_email'},
            'PHONE': {'SURVEY_MONKEY': '69079428', 'TRANSPARENT_CLASSROOM': 'first_parent_mobile_number'},
            'ADDRESS': {'SURVEY_MONKEY': '69078976', 'TRANSPARENT_CLASSROOM': 'first_parent_address'}
        },
        {
            'FIRST_NAME': {'SURVEY_MONKEY': '69079990', 'TRANSPARENT_CLASSROOM': 'second_parent_name.first'},
            'LAST_NAME': {'SURVEY_MONKEY': '77425213', 'TRANSPARENT_CLASSROOM': 'second_parent_name.last'},
            'EMAIL': {'SURVEY_MONKEY': '69079992', 'TRANSPARENT_CLASSROOM': 'second_parent_email'},
            'PHONE': {'SURVEY_MONKEY': '69079993', 'TRANSPARENT_CLASSROOM': 'second_parent_mobile_number'},
            'ADDRESS': {'SURVEY_MONKEY': '69079994', 'TRANSPARENT_CLASSROOM': 'second_parent_address'}
        }
    ],
    'CHILD': {
        'FIRST_NAME': {'SURVEY_MONKEY': '69082546', 'TRANSPARENT_CLASSROOM': 'child_name.first'},
        'LAST_NAME': {'SURVEY_MONKEY': '77425286', 'TRANSPARENT_CLASSROOM': 'child_name.last'},
        'DOB': {'SURVEY_MONKEY': '69082734', 'TRANSPARENT_CLASSROOM': 'child_birth_date'},
        'GENDER': {'SURVEY_MONKEY': '69083456', 'TRANSPARENT_CLASSROOM': 'child_gender'}
    },
    'SCHOOLS': {'SURVEY_MONKEY': '69085210'},
    'QUESTIONS': [
        {'SURVEY_MONKEY': '78278744', 'TRANSPARENT_CLASSROOM': 'ethnicity'},
        {'SURVEY_MONKEY': '78280009', 'TRANSPARENT_CLASSROOM': 'member_in_household'},
        {'SURVEY_MONKEY': '78282222', 'TRANSPARENT_CLASSROOM': 'income_2_member_household'},
        {'SURVEY_MONKEY': '78289530', 'TRANSPARENT_CLASSROOM': 'income_3_member_household'},
        {'SURVEY_MONKEY': '78290409', 'TRANSPARENT_CLASSROOM': 'income_4_member_household'},
        {'SURVEY_MONKEY': '78290754', 'TRANSPARENT_CLASSROOM': 'income_5_member_household'},
        {'SURVEY_MONKEY': '78291057', 'TRANSPARENT_CLASSROOM': 'income_6_member_household'},
        {'SURVEY_MONKEY': '78291263', 'TRANSPARENT_CLASSROOM': 'income_7_member_household'},
        {'SURVEY_MONKEY': '78291851', 'TRANSPARENT_CLASSROOM': 'income_8_member_household'},
        {'SURVEY_MONKEY': '78292095', 'TRANSPARENT_CLASSROOM': 'income_9_member_household'},
        {'SURVEY_MONKEY': '78292399', 'TRANSPARENT_CLASSROOM': 'income_10_member_household'},
        {'SURVEY_MONKEY': '69092809', 'TRANSPARENT_CLASSROOM': 'how_hear'},
        {'SURVEY_MONKEY': '69092811', 'TRANSPARENT_CLASSROOM': 'caregivers'},
        {'SURVEY_MONKEY': '69092815', 'TRANSPARENT_CLASSROOM': 'siblings'},
        {'SURVEY_MONKEY': '69092816', 'TRANSPARENT_CLASSROOM': 'disposition'},
        {'SURVEY_MONKEY': '69092817', 'TRANSPARENT_CLASSROOM': 'social_style'},
        {'SURVEY_MONKEY': '69092820', 'TRANSPARENT_CLASSROOM': 'parenting_style'},
        {'SURVEY_MONKEY': '69092823', 'TRANSPARENT_CLASSROOM': 'typical_weekday'},
        {'SURVEY_MONKEY': '69092825', 'TRANSPARENT_CLASSROOM': 'typical_weekend'},
        {'SURVEY_MONKEY': '69092827', 'TRANSPARENT_CLASSROOM': 'ideal_school'},
        {'SURVEY_MONKEY': '69092836', 'TRANSPARENT_CLASSROOM': 'other_schools'},
        {'SURVEY_MONKEY': '69092837', 'TRANSPARENT_CLASSROOM': 'montessori'},
        {'SURVEY_MONKEY': '69092839', 'TRANSPARENT_CLASSROOM': 'what_age'},
        {'SURVEY_MONKEY': '69092840', 'TRANSPARENT_CLASSROOM': 'specialists'},
        {'SURVEY_MONKEY': '69092841', 'TRANSPARENT_CLASSROOM': 'involvement'},
        {'SURVEY_MONKEY': '69092842', 'TRANSPARENT_CLASSROOM': 'enrich'},
        {'SURVEY_MONKEY': '69092843', 'TRANSPARENT_CLASSROOM': 'anything_else'}
    ]
}
