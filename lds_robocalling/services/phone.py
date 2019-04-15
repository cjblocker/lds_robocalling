from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import toml
import logging

from ..utils import export
from .. import _config

_logger = logging.getLogger('lds_robocalling.services.phone')
_config = _config['phone']
_client = Client(_config['account_sid'], _config['auth_token'])

def clean_number(number):
    if number is None:
        return ''
    elif number.startswith('+1'):
        number = number[2:]
    elif number.startswith('1'):
        number = number[1:]
    return ''.join(c for c in number if c.isdigit())

def compare_numbers(num1,num2):
    return clean_number(num1) == clean_number(num2)

@export
def national_format(num):
    num = clean_number(num)
    return '({}) {}-{}'.format(num[:3], num[3:6],num[6:])

from . import db
_phone_book = db.get_phone_book()

@export
def text(self, body, to=None):
    if to is None: to = _config['admin_number']
    to = clean_number(to)
    message = _client.messages.create(body=body, to=to, from_=_config['phone_number']) 

@export
def lookup(number):
    number = clean_number(number)
    if len(number) < 8:
        return number,'invalid'
    elif national_format(number) in _phone_book:
        return number, _phone_book[national_format(number)]
    try:
        number_data = _client.lookups.phone_numbers.get(number).fetch(add_ons='twilio_carrier_info')
        number_data.phone_number 
        _phone_book[national_format(number)] = number_data.add_ons['results']['twilio_carrier_info']['result']['carrier']['type']
        db.add_phone_type(national_format(number), _phone_book[national_format(number)])
    except TwilioRestException as e:
        if e.code == 20404:
            return number, 'invalid'
        else:
            raise e
    # print(number, number_data.add_ons['results']['twilio_carrier_info']['result']['carrier']['type'])
    return number, number_data.add_ons['results']['twilio_carrier_info']['result']['carrier']['type']

        