import yagmail
import datetime

from .log import logging
_logger = logging.getLogger('lds_robocalling.utils.email_api')
# https://github.com/kootenpv/yagmail

'''
import yagmail
yag = yagmail.SMTP()
contents = ['This is the body, and here is just text http://somedomain/image.png',
            'You can find an audio file attached.', '/local/path/song.mp3']
yag.send('to@someone.com', 'subject', contents)
'''

_default_email = "annarborysa"
_default_admin_email = 'cameronjblocker@gmail.com'

class EmailClient():
	"""EmailClient based on yagmail for sending emails
	through GMail"""
	def __init__(self, email=None, admin=None):
		self.email = email or _default_email
		self.admin = admin or _default_admin_email
		self.client = yagmail.SMTP(self.email)
		_logger.debug("Email Client Initialized")

	def new_member_alert(self,new_member_list, old_member_list=None):
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
				body += "{gender: <7} {name} {surname}\n\n".format(**mem)
		

		body += "Thank You,\nAnn Arbor YSA\n\nThis is an automated message"
		self.client.send(to=self.admin,
						subject="Ward Membership Changes {}".format(datetime.datetime.today()),
						contents=body);
		_logger.debug("Sent Ward Membership Change Email")

	def send_email(self, subject, body, to):
		self.client.send(to=to, subject=subject, contents=body);


