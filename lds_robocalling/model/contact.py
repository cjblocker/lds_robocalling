from ..services.phone import national_format
from ..services import phone 

CONTACT_PREF = {'TEXT', 'CALL', 'EMAIL', 'LETTER', 'FACEBOOK'}

class ContactCard(object):
    """Hold information relating to a members
    contact preference, such as email, phone,
    and address"""
    def __init__(self, db_dict={}, change_log={}):
        super(ContactCard, self).__init__()

        self._pref = db_dict.get('contact_pref', None)
        
        self._phone = db_dict.get('phone', None)
        self._phone_type = db_dict.get('phone_type', None)

        self._email = db_dict.get('email', None)

        self._fbid = db_dict.get('fbid', None)

        self._streetAddr1 = db_dict.get('streetAddr1', None)
        self._streetAddr2 = db_dict.get('streetAddr2', None)
        self._city = db_dict.get('city', None)
        self._state = db_dict.get('state', None)
        self._latitude = db_dict.get('latitude', None)
        self._longitude = db_dict.get('longitude', None)

        self._change_log = change_log

    def _set_pref(self, pref):
        pref = pref.upper()
        if pref not in CONTACT_PREF:
            raise ValueError(f'{pref} is not a valid contact preference')
        if pref != self._pref:
            self._pref = pref
            self._change_log['contact_pref'] = self._pref

    def _set_phone(self, phn_num):
        phn_num = national_format(phn_num)
        if phn_num != self._phone:
            self._phone = phn_num
            self._change_log['phone'] = self._phone

            self._phone_type = phone.lookup(self._phone)
            self._change_log['phone_type'] = self._phone_type

    def _set_email(self, email):
        if '@' not in email[1:] or '.' not in email[3:]: #this is a lazy check, should do re
            raise ValueError(f'{email} is not a valid email address')
        if email != self._email:
            self._email = email 
            self._change_log['email'] = self._email

    def _set_fbid(self, fbid):
        if fbid != self._fbid:
            self._fbid = fbid
            self._change_log['fbid'] = self._fbid

    def _set_streetAddr1(self, streetAddr1):
        if streetAddr1 != self._streetAddr1:
            self._streetAddr1 = streetAddr1
            self._change_log['streetAddr1'] = self._streetAddr1

    def _set_streetAddr2(self, streetAddr2):
        if streetAddr2 != self._streetAddr2:
            self._streetAddr2 = streetAddr2
            self._change_log['streetAddr2'] = self._streetAddr2

    def _set_city(self, city):
        if city != self._city:
            self._city = city
            self._change_log['city'] = self._city

    def _set_state(self, state):
        if state != self._state:
            self._state = state
            self._change_log['state'] = self._state

    def _set_latitude(self, latitude):
        if latitude != self._latitude:
            self._latitude = latitude
            self._change_log['latitude'] = self._latitude

    def _set_longitude(self, longitude):
        if longitude != self._longitude:
            self._longitude = longitude
            self._change_log['longitude'] = self._longitude


    pref = property(fget=lambda self: self._pref, fset=_set_pref)
    phone = property(fget=lambda self: self._phone, fset=_set_phone)
    phone_type = property(fget=lambda self: self._phone_type, fset=lambda self, x: None)
    email = property(fget=lambda self: self._email, fset=_set_email)
    fbid = property(fget=lambda self: self._fbid, fset=_set_fbid)
    streetAddr1 = property(fget=lambda self: self._streetAddr1, fset=_set_streetAddr1)
    streetAddr2 = property(fget=lambda self: self._streetAddr2, fset=_set_streetAddr2)
    city = property(fget=lambda self: self._city, fset=_set_city)
    state = property(fget=lambda self: self._state, fset=_set_state)
    latitude = property(fget=lambda self: self._latitude, fset=_set_latitude)
    longitude = property(fget=lambda self: self._longitude, fset=_set_longitude)

        