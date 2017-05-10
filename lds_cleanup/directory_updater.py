from datetime import date
from timeit import default_timer as time 

import toml

from email_api import EmailClient
from database import Database, DATE_FORMAT
from phone_api import PhoneBook, compare_numbers
from lds_scraper import LDSDirectoryScraper

from log import logging, log_call
_logger = logging.getLogger('lds_cleanup.directory_updater')

## TODO:
# Add database transaction for faster updating
# Way to save other attributes
# Make the phone numbers all look the same


def create_new_member(member, phone_book):
    phone, phone_type = phone_book.lookup(member['phone'])
    # del member['callings']
    member.update({
        'phone': phone, #This is a subtle bug
        'base_score':1 if member['callings'] else 0,#1
        'phone_type':phone_type,
        'sms_pref':phone_type == 'mobile' or phone_type=='voip',
        'email_pref':phone_type == 'landline' or phone_type=='invalid',
        'call_pref':False,
        'date_added':DATE_FORMAT.format(date.today()),
        'days_helped':[],
        'blackout_days':[],
        'scheduled':''
    })
    _logger.info("Added {ID: >12}: {name} {surname} {phone} {phone_type}".format(**member))
    del member['callings']
    return member 

def update_current_member(ldsorg_data, db_data, phone_book):
    del ldsorg_data['callings']
    change_log = []
    # ldsorg_data['scheduled'] = '' #quick way to delete everyones schedule
    for key in ldsorg_data.keys():
        try:
            db_data[key]
        except KeyError as e:
            db_data[key] = None

        if db_data[key] == ldsorg_data[key]:
            del ldsorg_data[key]
        elif key == 'phone' and not compare_numbers(db_data[key],ldsorg_data[key]):
            phone, phone_type = phone_book.lookup(ldsorg_data['phone'])
            ldsorg_data['phone'] = phone
            #this can/will be deleted in a following loop iteration if it's not new
            ldsorg_data['phone_type'] = phone_type 
            change_log.append("{} => {}".format(db_data[key],ldsorg_data[key]))
        else:
            change_log.append("{} => {}".format(db_data[key],ldsorg_data[key]))
    if change_log:
        _logger.info("Updated {ID: >12}: {name} {surname}\n".format(**db_data) + "\n".join(change_log))
    return ldsorg_data

@log_call(_logger)
def update():
    config = toml.load('config.toml')

    ldsorg = LDSDirectoryScraper(config['lds_org_username'])
    db = Database(config['database'])
    phone_book = PhoneBook(config['phone'])

    # We save about a minute by getting all members at once
    # instead of getting each one as we need it
    db_member_data = db.get_all_members()
    if db_member_data:
        current_keys = list(db_member_data.keys())
    else:
        current_keys = []
    new_members = []

    for member in ldsorg.get_ward_member_generator():
        member_info = ldsorg.get_member_info(member['ID'])
        if str(member['ID']) in current_keys:
            current_keys.remove(member['ID'])
            updated = update_current_member(member_info, db_member_data[member['ID']] ,phone_book)   
        else:
            member.update(member_info)
            updated = create_new_member(member, phone_book)
            new_members.append(updated)

        if updated:
            updated.update({'ID':member['ID']})
            db.save_member(updated)

    if new_members or current_keys:
        old_members = []
        for memID in current_keys:
            old_members.append(db_member_data[memID])
            db.delete_member(db_member_data[memID])
            _logger.info("Removed {ID: >12}: {name} {surname}".format(**db_member_data[memID]))

        email = EmailClient()
        email.new_member_alert(new_members, old_members)


if __name__ == '__main__':
    t = time()
    update()
    m, s = divmod(round(time()-t), 60)
    _logger.info("It took {:.0f} minutes {:.0f} seconds to update the directory".format(m,s))