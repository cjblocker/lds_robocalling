from phone_api import national_format, PhoneBook

_phone_book = PhoneBook()

CONTACT_PREF = {'TEXT', 'CALL', 'EMAIL', 'LETTER', 'FACEBOOK'}

class ContactCard(object):
    """Hold information relating to a members
    contact preference, such as email, phone,
    and address"""
    def __init__(self, db_dict={}, change_log={}):
        super(ContactCard, self).__init__()

        self._pref = db_dict.get('pref', None)
        
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

    def set_pref(self, pref):
        pref = pref.upper()
        if pref not in CONTACT_PREF:
            raise ValueError(f'{pref} is not a valid contact preference')
        if pref != self._pref:
            self._pref = pref
            self._change_log['pref'] = self._pref
    pref = property(fget=lambda self: self._pref, fset=set_pref)

    def set_phone(self, phn_num):
        phn_num = national_format(phn_num)
        if phn_num != self._phone:
            self._phone = phn_num
            self.change_log['phone'] = self._phone

            self._phone_type = _phone_book.lookup(self._phone)
            self._change_log['phone_type'] = self._phone_type
    phone = property(fget=lambda self: self._phone, fset=set_phone)
    phone_type = property(fget=lambda self: self._phone_type, fset=lambda self, x: None)

    def set_email(self, email):
        if '@' not in email[1:] or '.' not in email[3:]: #this is a lazy check, should do re
            raise ValueError(f'{email} is not a valid email address')
        if email != self._email:
            self._email = email 
            self._change_log['email'] = self._email
    email = property(fget=lambda self: self._email, fset=set_email)

    def set_fbid(self, fbid):
        if fbid != self._fbid:
            self._fbid = fbid
            self._change_log['fbid'] = self._fbid
    fbid = property(fget=lambda self: self._fbid, fset=set_fbid)

    def set_streetAddr1(self, streetAddr1):
        if streetAddr1 != self._streetAddr1:
            self._streetAddr1 = streetAddr1
            self._change_log['streetAddr1'] = self._streetAddr1
    streetAddr1 = property(fget=lambda self: self._streetAddr1, fset=set_streetAddr1)

    def set_streetAddr2(self, streetAddr2):
        if streetAddr2 != self._streetAddr2:
            self._streetAddr2 = streetAddr2
            self._change_log['streetAddr2'] = self._streetAddr2
    streetAddr2 = property(fget=lambda self: self._streetAddr2, fset=set_streetAddr2)

    def set_city(self, city):
        if city != self._city:
            self._city = city
            self._change_log['city'] = self._city
    city = property(fget=lambda self: self._city, fset=set_city)

    def set_state(self, state):
        if state != self._state:
            self._state = state
            self._change_log['state'] = self._state
    state = property(fget=lambda self: self._state, fset=set_state)

    def set_latitude(self, latitude):
        if latitude != self._latitude:
            self._latitude = latitude
            self._change_log['latitude'] = self._latitude
    latitude = property(fget=lambda self: self._latitude, fset=set_latitude)

    def set_longitude(self, longitude):
        if longitude != self._longitude:
            self._longitude = longitude
            self._change_log['longitude'] = self._longitude
    longitude = property(fget=lambda self: self._longitude, fset=set_longitude)



        