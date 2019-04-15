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
_directory_member_list_url = 'https://www.lds.org/directory/services/web/v3.0/mem/member-list/{unit_num}' # Lists members names, IDs, and gender
_ysa_list_url = r'https://www.lds.org/mls/mbr/services/orgs/sub-orgs-with-callings?lang=eng&subOrgId=1140320' # YSA list with age, phone, email 
_member_household_url = 'https://www.lds.org/directory/services/web/v3.0/mem/householdProfile/{ID}?imageSize=MEDIUM' # Get info about a particular member, including contact, geolocation, calling, etc (no age)
_unit_list_url = r'https://www.lds.org/directory/services/web/v3.0/unit/current-user-units/' # Get information about units your in
_search_name_url = 'https://www.lds.org/mls/mbr/services/member-lookup?includeEmailAndPhoneSearch=true&includeOutOfUnitMembers=true&lang=eng&term={}' # Get information about a particular member by name, includes email, phone, gender, age
_member_profile_url = 'https://www.lds.org/mls/mbr/records/member-profile/service/{ID}?lang=eng' # Includes age, but lacks longitude, latitude, calling
_member_callings_url = 'https://www.lds.org/mls/mbr/records/member-profile/callings-and-classes/{ID}?lang=eng' # Gets a lot of information about an individuals callings and classes
_htvt_url = 'https://www.lds.org/htvt/services/v1/{unit_num}/members/individualProfile/{ID}/{ID}' # Returns IDs of home and visiting teachers
_my_id_url = 'https://www.lds.org/directory/services/web/v3.0/mem/current-user-info/' # returns current user's ID
_member_list_url = 'https://www.lds.org/mls/mbr/services/report/member-list?lang=eng&unitNumber={unit_num}'
_recent_convert_url = 'https://www.lds.org/mls/mbr/services/report/new-member/unit/{unit_num}/12?lang=eng'

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



class LDSorgScraper():
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
        raw_list = self.scrape( _directory_member_list_url.format(unit_num=(unit_num or self.unit_num)) ).json()
        for house in raw_list:
            member = {
                'surname' : house['headOfHouse']['surname'],
                'name' : house['headOfHouse']['directoryName'],
                'gender' : house['headOfHouse']['gender'],
                'ID' : str(house['headOfHouseIndividualId']),
            }
            yield member

    def get_ysa_member_list(self):
        raw_list = self.scrape( _ysa_list_url ).json()[0]['members']
        res =[]
        for mem in raw_list:
            name = mem['spokenName'].split(' ')
            member = {
                'ID' : mem['id'],
                'name' : name[0],
                'surname': name[-1],
                'gender': 'MALE' if mem['genderLabelShort'] == 'M' else 'FEMALE',
                'birthdate' : mem['birthDate'],
                'email' : mem['email'] or mem['householdEmail'],
                'phone' : mem['phone'] or mem['householdPhone'],
            }
            member.update(self.get_member_info(mem['id']))
            res.append(member)
        return res 

    def get_member_info(self, ID):
        try:
            member = self.scrape(_member_household_url.format(ID=ID)).json()
        except:
            return {'phone':'', 'email':'', 'callings':[]}
        member_data = {
            'phone': member['headOfHousehold']['phone'] or member['householdInfo']['phone'],
            'email': member['headOfHousehold']['email'] or member['householdInfo']['email'],
            'callings': member['headOfHousehold']['callings'],
            # 'address': {
            #     # 'street1': member['householdInfo']['address']['addr1'],
            #     # 'street2': member['householdInfo']['address']['addr2'],
            #     # 'city': member['householdInfo']['address']['city'],
            #     # 'state': member['householdInfo']['address']['state'],
            #     # 'zip': member['householdInfo']['address']['postal'],
            #     # 'longitude': member['householdInfo']['address']['longitude'],
            #     # 'latitude': member['householdInfo']['address']['latitude']
            # }
        }
        return member_data

    def get_member_photo(self, ID):
        """ this is just a stub, shows the image instead of returning it, not sure how I want to interface it"""
        member = self.scrape(_member_household_url.format(ID=ID)).json()
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

    def get_recent_convert_ids(self):
        raw_list = self.scrape(_recent_convert_url.format(unit_num=self.unit_num)).json()
        return [mem['id'] for mem in raw_list]

    def get_member_list(self):
        """ Just basic info on each member"""
        res = []
        raw_list = self.scrape(_member_list_url.format(unit_num=self.unit_num)).json()
        for mem in raw_list:
            surname = mem['name'].split(', ')[0]
            member_data = {
                'name': mem['givenName'],
                'surname': surname,
                'gender': mem['gender'],
                'birthDate': mem['birthDate'],
                'ID': mem['id']
            }
            res.append(member_data)
        return res 

