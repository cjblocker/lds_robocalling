import yagmail
import datetime

import logging
_logger = logging.getLogger('hollyg.services.email')

from ..utils import export
from .. import _config
_config = _config['email']
_client = yagmail.SMTP(_config['user'])
# https://github.com/kootenpv/yagmail

'''
import yagmail
yag = yagmail.SMTP()
contents = ['This is the body, and here is just text http://somedomain/image.png',
            'You can find an audio file attached.', '/local/path/song.mp3']
yag.send('to@someone.com', 'subject', contents)
'''

def send_email(to, subject, body):
	_client.send(to=to, subject=subject, contents=body);


def new_member_alert(new_member_list, old_member_list=None):
	body = "Hello,\n\n"
	if new_member_list:
		if type(new_member_list) != list: new_member_list = list(new_member_list)
		body += "<b>The following new members were added to your ward:</b>\n\n"
		for mem in new_member_list:
			body += "{gender: <7} {name} {surname}\n\n".format(**mem)

	if old_member_list:
		if type(old_member_list) != list: old_member_list = list(old_member_list)
		body += "<b>The following members left your ward:</b>\n\n"
		for mem in old_member_list:
			body += "{gender: <7} {name} {surname}\n\n".format(gender=mem.gender, name=mem.name, surname=mem.surname)
	

	body += "Thank You,\nAnn Arbor YSA\n\nThis is an automated message"
	send_email(to=_config['admin_email'],
					subject="Ward Membership Changes {}".format(datetime.datetime.today()),
					body=body);
	_logger.debug("Sent Ward Membership Change Email")



