"""LDS.org Ward Directory Scraper

Data retrieved from lds.org is subject to their copyright restriction:
| @ Copyright The Church of Jesus Christ of Latter-day Saints, 2017 All rights reserved. 
| Information and data may only be used for conducting official church business. All other 
| usage must be granted by written consent by The Church of Jesus Christ of Latter-day Saints.'
"""
import requests
import keyring
import getpass

from PIL import Image

_login_url=r'https://ident.lds.org/sso/UI/Login?service=credentials'
_directory_url = r'https://www.lds.org/directory/?lang=eng'
_member_list_url = 'https://www.lds.org/directory/services/web/v3.0/mem/member-list/{}'
_member_url = 'https://www.lds.org/directory/services/web/v3.0/mem/householdProfile/{}?imageSize=MEDIUM'
_unit_list_url = r'https://www.lds.org/directory/services/web/v3.0/unit/current-user-units/'

_a2ysa_unit_num = 200549
_keyring_system_id = 'ldsorg'


# TODO: Some of these headers are probably not necessary
_headers = {
    'Origin':'https://ident.lds.org',
    'X-DevTools-Emulate-Network-Conditions-Client-Id':'b145e9bc-bdf5-4572-85d5-474be5374693',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Content-Type':'application/x-www-form-urlencoded',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer':'https://ident.lds.org/sso/UI/Login?service=credentials&error=authfailed',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'en-US,en;q=0.8,km;q=0.6',
}



class LDSDirectoryScraper():
    """Scraper for LDS.org ward directories
    This was created for a YSA ward, where every member is the head of household
    so it only returns information on the head of household, though it could most
    likely be easily extended.
    """
    def __init__(self, username=None, password=None, unit_num=_a2ysa_unit_num, wait2login=False):
        self.session = requests.session()
        self.username = username
        self.password = password
        if not wait2login: self.login()
        self.unit_num = unit_num

    def scrape(self,url,stream=False):
        r = self.session.get( url, headers = _headers, stream=stream)
        r.raise_for_status()
        if 'ident' in r.url:
        	self.login()
        	r = self.session.get( url, headers = _headers, stream=stream)
        	r.raise_for_status()
        return r

    def login(self,username=None, password=None):
        if self.username is None:
            self.username = raw_input("Please Enter Your LDS.org Username:")
        if self.password is None:
            self.password = self.get_password(self.username)

        login_payload = {
            'IDButton':'Log In',
            'IDToken1':self.username,
            'IDToken2':self.password,
            'SunQueryParamsString':'c2VydmljZT1jcmVkZW50aWFscw==',
            'encoded':'false',
            'goto':_directory_url,
            'gotoOnFail':'',
            'gx_charset':'UTF-8'
        }

        self.session.get(_login_url)
        self.session.post(_login_url, data = login_payload, headers = _headers)

    def get_password(self,username):
        password = keyring.get_password(_keyring_system_id,username)
        if password is None:
            password = getpass.getpass("Enter your lds.org password for {}:".format(username))
            keyring.set_password(_keyring_system_id,username,password)
        return password 

    def get_ward_member_generator(self,unit_num=None):
        raw_list = self.scrape( _member_list_url.format(unit_num or self.unit_num) ).json()
        for house in raw_list:
            member = {
                'surname' : house['headOfHouse']['surname'],
                'name' : house['headOfHouse']['directoryName'],
                'gender' : house['headOfHouse']['gender'],
                'ID' : str(house['headOfHouseIndividualId']),
            }
            yield member

    def get_member_info(self, ID):
        member = self.scrape(_member_url.format(ID)).json()
        member_data = {
            'phone': member['headOfHousehold']['phone'] or member['householdInfo']['phone'],
            'email': member['headOfHousehold']['email'] or member['householdInfo']['email'],
            'callings': member['headOfHousehold']['callings']
        }
        return member_data

    def get_member_photo(self, ID):
        """ this is just a stub, shows the image instead of returning it, not sure how I want to interface it"""
        member = self.scrape(_member_url.format(ID)).json()
        r = self.scrape(member['headOfHousehold']['photoUrl'] or member['householdInfo']['photoUrl'],stream=True)
        r.raw.decode_content = True  # Required to decompress gzip/deflate compressed responses.
        with Image.open(r.raw) as img:
            img.show()
        r.close()  

    def get_member_id_by_name(self, name, surname):
    	"""This is an expensive operation as we download the whole ward directory and then perform a linear
    	search for the name. We could speed it up by using the fact that the result is ordered alphabetically"""
    	name = name.lower()
    	surname = surname.lower()
    	for member in self.get_ward_member_generator():
    		if name in member['name'].lower().split(" ") and surname == member['surname'].lower():
    			return member['ID']
    	return -1

