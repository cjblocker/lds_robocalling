from lds_cleanup.database import Database 
from lds_cleanup.log import logging, log_call

from lds_cleanup.directory_updater import main as update_directory
from lds_cleanup.scheduler import main as run_scheduler
from lds_cleanup.fb_update import update_member_fb_data


_logger = logging.getLogger('CL tool')
db = Database()

@log_call(_logger)
def clear_all_assignments():
    members = db.get_all_members()
    for mem in members.values():
        if mem['scheduled'] != '' and mem['scheduled'] != '-':
            db.save_member({'ID':mem['ID'], 'scheduled':''})

@log_call(_logger)
def write_data(name, surname, field, data):
    mem = db.get_member_by_name(name, surname)
    db.save_member({'ID':mem['ID'], field:data})

