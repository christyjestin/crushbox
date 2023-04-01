from collections import defaultdict
import re, os
from dotenv import load_dotenv

from flask import Flask, request

from twilio.rest import Client as TwilioClient
from twilio.twiml.messaging_response import MessagingResponse

# setup Twilio
load_dotenv('test.env')
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = TwilioClient(account_sid, auth_token)

crush_dict = defaultdict(set)

ENDS_IN_US_PHONE_NUMBER_REGEX = re.compile(r'.*[2-9]{1}[0-9]{2}[2-9]{1}[0-9]{6}$')
PHONE_NUMBER_LENGTH = 10

TWILIO_NUMBER = '8667941693'
US_COUNTRY_CODE = '+1'

HELP_TEXT = '''Please use the following commands to add a crush, delete a crush, \
delete all crushes, list all crushes, or see this help text again:
ADD XXX-XXX-XXXX
DELETE XXX-XXX-XXXX
DELETE ALL
LIST
HELP

N.B. the commands are NOT case sensitive.'''

ERROR_TEXT = 'I\'m sorry; I don\'t recognize this command.'

INTRO_TEXT = '''Welcome to Crushbox! It's simple: send Crushbox your crushes (just their \
phone numbers - not their names), and if there's a mutual crush, then we'll let you know.'''

def ends_in_valid_phone_number(string):
    return bool(ENDS_IN_US_PHONE_NUMBER_REGEX.fullmatch(string))

def with_country_code(number):
    return US_COUNTRY_CODE + number

# returns mutual crush message if it's mutual and message about adding otherwise
def add_crush(crusher, crush):
    crush_dict[crusher].add(crush)
    if crush not in crush_dict:
        alert_new_potential_user(crush)
    elif crusher in crush_dict[crush]:
        alert_new_match(msg_recipient = crush, match = crusher)
        return f'You and {crush} have a crush on each other'
    return f'{crush} has been added to crushes!'

def delete_all(crusher):
    crush_dict[crusher].clear()

def delete_crush(crusher, crush):
    crush_dict[crusher].discard(crush)

def list_crushes(crusher):
    return list(crush_dict[crusher])

# alert the original crusher in a new match
def alert_new_match(msg_recipient, match):
    twilio_client.messages.create(
        body = f'You and {match} have a crush on each other!',
        from_ = with_country_code(TWILIO_NUMBER),
        to = with_country_code(msg_recipient)
    )

# alert a crush who is not on Crushbox yet
def alert_new_potential_user(number):
    twilio_client.messages.create(
        body = 'Someone on Crushbox has a crush on you!\n',
        from_ = with_country_code(TWILIO_NUMBER),
        to = with_country_code(number)
    )
    twilio_client.messages.create(
        body = INTRO_TEXT,
        from_ = with_country_code(TWILIO_NUMBER),
        to = with_country_code(number)
    )
    twilio_client.messages.create(
        body = HELP_TEXT,
        from_ = with_country_code(TWILIO_NUMBER),
        to = with_country_code(number)
    )

# adds intro text if the crusher is a new user
def error_msg(crusher):
    if crusher in crush_dict:
        msg = ERROR_TEXT + '\n' + HELP_TEXT
    # new user message
    else:
        msg = INTRO_TEXT + '\n' + ERROR_TEXT + '\n' + HELP_TEXT
    return msg

app = Flask(__name__)

@app.route('/sms', methods=['GET', 'POST'])
def incoming_sms():
    resp = MessagingResponse()
    body = request.values.get('Body')
    crusher = request.values.get('From')[-PHONE_NUMBER_LENGTH:]
    print(f'body: {body}')
    print(f'crusher: {crusher}')
    # cast all characters to uppercase and remove punctuation
    cleaned_body = re.sub(r'[^\w]', '' , body.upper())
    print(cleaned_body)

    # handle commands that require a phone number as input
    if ends_in_valid_phone_number(cleaned_body):
        crush = cleaned_body[-PHONE_NUMBER_LENGTH:]
        if cleaned_body.startswith('ADD'):
            # self crush
            if crush == crusher:
                msg = 'Excellent choice if I do say so myself ;)'
            else:
                msg = add_crush(crusher, crush)
            resp.message(msg)
        elif cleaned_body.startswith('DELETE'):
            delete_crush(crusher, crush)
            resp.message(f'{crush} has been deleted from crushes.')
        else:
            resp.message(error_msg(crusher))
    # handle commands that don't require a phone number as input
    else:
        if cleaned_body.startswith('DELETEALL'):
            delete_all(crusher)
            resp.message('All crushes have been deleted.')
        elif cleaned_body.startswith('LIST'):
            crushes = list_crushes(crusher)
            resp.message('Your crushes are: \n' + '\n'.join(crushes))
        elif cleaned_body.startswith('HELP'):
            resp.message(HELP_TEXT)
        else:
            resp.message(error_msg(crusher))

    print(crush_dict)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)