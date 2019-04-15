from .contact import ContactCard

GENDER = {'MALE','FEMALE'}
GROUP = {
            'ACTIVE',   # Active members, come to church
            'RC',       # Recent Converts, confirmed within past year
            'LA',       # Less Active, willing to meet, but don't come to church
            'DNC',      # Do Not Contact, someone who doesn't want us to bug them
            'UNKNOWN'   # We don't know who this is
        }
DATE_FORMAT = '{:%Y-%m-%d}'

class Member(object):
    """Class to represent a member in the ward

    This is the primary enforcer of keeping the
    database data clean and of the correct type."""
    def __init__(self, db_dict={}):
        super(Member, self).__init__()
        self._name       = db_dict.get('name',None)
        self._surname    = db_dict.get('surname',None)

        self._id         = db_dict.get('ID',None)
        self._group      = db_dict.get('group', None)
        self._birthdate  = db_dict.get('birthdate',None)
        self._date_added = db_dict.get('date_added',None)
        self._gender     = db_dict.get('gender',None)

        self._ht = db_dict.get('ht', [])
        self._vt = db_dict.get('vt', [])

        self._change_log = {}
        self.contact = ContactCard(db_dict, self._change_log)

    def as_legacy_dict(self):
        return {
            'name': self._name,
            'surname': self._surname,
            'ID': self._id,
            'phone': self.contact.phone,
            'phone_type': self.contact.phone_type,
            'email': self.contact.email,
            'callings': [],
        }

    def set_name(self, name):
        name = name.split(',')[-1]
        if name != self._name:
            self._name = name
            self._change_log['name'] = self._name
    name = property(fget=lambda self: self._name, fset=set_name)

    def set_surname(self, surname):
        if surname != self._surname:
            self._surname = surname
            self._change_log['surname'] = self._surname
    surname = property(fget=lambda self: self._surname, fset=set_surname)

    def set_id(self, id):
        if id != self._id:
            self._id = id
            self._change_log['ID'] = self._id
    id = property(fget=lambda self: self._id, fset=set_id)

    def set_birthdate(self, birthdate):
        if birthdate != self._birthdate:
            self._birthdate = birthdate
            self._change_log['ID'] = self._birthdate
    birthdate = property(fget=lambda self: self._birthdate, fset=set_birthdate)

    def set_group(self, grp):
        grp = grp.upper()
        if grp not in GROUP:
            raise ValueError(f"{grp} is not a valid group identifier") 

        if grp != self._group:
            self._group = grp

    group = property(lambda self:self._group, set_group)

    def set_gender(self, gndr):
        gndr = gndr.upper()
        if gndr == 'M': gndr = 'MALE'
        elif gndr == 'F': gndr = 'FEMALE'
        if gndr not in GENDER:
            raise ValueError(f"{gndr} is not a valid gender identifier")

        if gndr != self._gender:
            self._gender = gndr 

    gender = property(lambda self:self._gender, set_gender)

    @property
    def age(self):
        """ Lazy evaluation of age """
        if self._age:
            return self._age
        else:
            self._age = 0
            return self._age 
