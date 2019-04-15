from .database import Database 
from .lds_scraper import LDSorgScraper
from .facebook import get_fb_group_members
from ..model.member import Member

def add_new_members(mems):
    """ This should look for new members and create
    member objects with the basic things that don't
    change much such as there name, surname, id,
    gender, birthday, date_added, and possibly group
    """
    ldsorg = LDSorgScraper()
    rc_list = ldsorg.get_recent_convert_ids() #TODO This may be permissions specific
    member_records = ldsorg.get_member_list()
    for mem in member_records:
        if mem['ID'] not in mems.keys(): 
            # We have a new member
            new_mem = Member()
            new_mem.id = mem['ID']
            new_mem.name = mem['name']
            new_mem.surname = mem['surname']
            new_mem.gender = mem['gender']
            new_mem.birthdate = mem['birthDate']
            if new_mem.id in rc_list:
                new_mem.group = 'RC'
            else: # New members are either recent converts or move-ins
                new_mem.group = 'UNKNOWN'
            mems[new_mem.id] = new_mem
    return mems

def update_church_details(mems):
    return mems

def update_contact_info(mems):
    """ This verifys phone, email and address are all
    up-to-date with the online directory and records.
    """
    return mems

def update_facebook_id(mems):
    """ This will try to find members of the ward in 
    the ward facebook group, and if found will add
    their facebook ID to their profile. It will also
    update names to be consistant with facebook
    """
    fb_group = get_fb_group_members()
    for mem in mems.values():
        try:
            sur_group = fb_group[mem.surname]
        except KeyError as e:
            continue # Their last name doesn't match
                     # anybody we know so move on

        try:
            mem_id = sur_group[mem.name]
            # Simple Success!
            mem.contact.fbid = mem_id
        except KeyError as e:
            # So last names match but first don't exactly
            # We'll run through each one and check
            for name, fbid in sur_group.items():
                if name.lower() in mem.name.lower() or
                   mem.name.lower() in name.lower():
                   # Is one name a shortened version of another?
                   mem.contact.fbid = fbid
                   mem.name = name
                elif name.lower()[:3] in mem.name.lower() or
                   mem.name.lower()[:3] in name.lower():
                   # One last chance for a stub of the name
                   # but lets confirm with user
                   ans = input(f'{mem.name} {mem.surname} is {name} on facebook?').lower()
                   if ans == '' or ans == 'y':
                        mem.contact.fbid = fbid
                        mem.name = name
    return mems


def sync():
    db = Database()
    ward_mems = db.get_all_members()

    ward_mems = add_new_members(ward_mems)
    ward_mems = update_church_details(ward_mems)
    ward_mems = update_contact_info(ward_mems)
    ward_mems = update_facebook_id(ward_mems)

    db.save_members(ward_mems)