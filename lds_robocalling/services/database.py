import pyrebase # https://github.com/thisbejim/Pyrebase
import toml
from datetime import datetime

from .phone import national_format
import logging
_logger = logging.getLogger('hollyg.services.database')
from ..model import Member 

## TODO
# Create Database "Interface"
# Add transactioning
# Try out another database? local?
DATE_FORMAT = '{:%Y-%m-%d}'

class Database():
    """docstring for Database"""

    def __init__(self, config):
        config['serviceAccount'] = str(config['serviceAccount'])
        self.db = pyrebase.initialize_app(config).database()
        self.wait = False
        self.member = {}
        _logger.debug("Database Initialized")

    def get_member_by_id(self, ID):
        """Return a dictionary from the database corresponding to ID"""
        return Member(dict(self.db.child('member').child(ID).get().val()))

    def get_member_by_phone_number(self, num):
        num = national_format(num)
        try:
            res = self.db.child('member').order_by_child('phone').equal_to(num).get().val().values()[0]
        except IndexError:
            res = None
        return Member(res) if res else None

    def get_member_by_name(self, name, surname):
        try:
            res = self.db.child('member').order_by_child('surname').equal_to(surname).get().val().values()
            
            for r in res:
                if name.lower() in str(r.get('name')).lower():
                    return Member(r)
            return None
            
        except IndexError:
            return None

    def save_members(self, mem_list):
        if isinstance(mem_list, dict):
            mem_list = mem_list.values()
        for mem in mem_list:
            save_member(mem)

    def save_member(self, member):
        _logger.debug("Updating %s",member)
        self.db.child('metalog').child('member').child(member.id).update({DATE_FORMAT.format(datetime.now()):member._change_log})
        self.db.child('member').child(member.id).update(member._change_log)
        member._change_log = {}

    def get_member_ids(self):
        """Return a list of member ID numbers that are keys for database"""
        return self.db.child('member').shallow().get().each()

    def get_all_members(self):
        return [Member(mem) for mem in self.db.child('member').get().val().values()]

    def delete_member(self, member):
        _logger.debug("Deleting %s",member)
        self.db.child('member').child(member.id).remove()

    def add_membership_count(self, num):
        self.db.child('stat').child('membership').update({DATE_FORMAT.format(datetime.now()):num})

    def add_fb_count(self, num):
        self.db.child('stat').child('fb_count').update({DATE_FORMAT.format(datetime.now()):num})

    def add_fb_active_count(self, num):
        self.db.child('stat').child('fb_active_count').update({DATE_FORMAT.format(datetime.now()):num})

    def get_phone_book(self):
        return self.db.child('PhoneBook').get().val()

    def add_phone_type(self, phone_num, phone_type):
        self.db.child('PhoneBook').child(phone_num).update(phone_type)

