from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import toml

from .log import logging
_logger = logging.getLogger('lds_robocalling.utils.phone_api')

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

def national_format(num):
    num = clean_number(num)
    return '({}) {}-{}'.format(num[:3], num[3:6],num[6:])

class PhoneBook():
    """docstring for PhoneBook"""

    def __init__(self, config=None):
        if config is None: config = toml.load('config.toml')['phone']
        self.client = Client(config['account_sid'], config['auth_token'])

    def lookup(self,number):
        number = clean_number(number)
        if len(number) < 8:
            return number, 'invalid'
        try:
            number_data = self.client.lookups.phone_numbers.get(number).fetch(add_ons='twilio_carrier_info')
            number_data.phone_number 
        except TwilioRestException as e:
            if e.code == 20404:
                return number, 'invalid'
            else:
                raise e
        return number_data.national_format, number_data.add_ons['results']['twilio_carrier_info']['result']['carrier']['type']

class Phone():
    """docstring for Phone"""
    def __init__(self, config=None): 
        if config is None: config = toml.load('config.toml')['phone']
        self.client = Client(config['account_sid'], config['auth_token'])
        self.phone_number = config['phone_number']
        self.admin_number = config['admin_number']

    def text(self, body, to=None):
        if to is None: to = self.admin_number
        to = clean_number(to)
        message = self.client.messages.create(body=body, to=to, from_=self.phone_number) 

        