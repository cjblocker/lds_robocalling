import pyrebase # https://github.com/thisbejim/Pyrebase
import toml

from phone_api import national_format
from log import logging
_logger = logging.getLogger('lds_cleanup.database')

## TODO
# Create Database "Interface"
# Add transactioning
# Try out another database? local?
DATE_FORMAT = '{:%Y-%m-%d}'

class Database():
	"""docstring for Database"""

	def __init__(self, config=None):
		if config is None: config = toml.load('config.toml')['database']
		config['serviceAccount'] = str(config['serviceAccount'])
		self.db = pyrebase.initialize_app(config).database()
		self.wait = False
		self.member = {}
		_logger.debug("Database Initialized")

	def start_transaction(self): 
		print("This Function is not currently working!")
		assert( not self.wait) #TODO: Replace by throwing real error
		self.wait = True

	def close_transaction(self):
		print("This Function is not currently working!")
		self.db.update(self.member) # ERROR: This is doing a set, not update!
		self.member = {}
		self.wait = False

	def get_member_by_id(self, ID):
		"""Return a dictionary from the database corresponding to ID"""
		return dict(self.db.child('member').child(ID).get().val())

	def get_member_by_phone_number(self, num):
		num = national_format(num)
		try:
			res = self.db.child('member').order_by_child('phone').equal_to(num).get().val().values()[0]
		except IndexError:
			res = None
		return res 

	def get_member_by_name(self, name, surname):
		try:
			res = self.db.child('member').order_by_child('surname').equal_to(surname).get().val().values()
			# print res.get('name')
			# print res.get(u'name')
			if isinstance(res,list):
				for r in res:
					if name.lower() in str(r.get('name')).lower():
						return r
				return None
			else:
				print 'This is never run'
				if name.lower() in str(res.get('name')).lower():
					return res
				else:
					return None
			
		except IndexError:
			return None

	def save_member(self, member):
		_logger.debug("Updating %s",member)
		if not self.wait:
			self.db.child('member').child(member['ID']).update(member)
		else:
			self.member.update({r'member/'+member['ID']+r'/':member})

	def get_member_ids(self):
		"""Return a list of member ID numbers that are keys for database"""
		return self.db.child('member').shallow().get().each()

	def get_all_members(self):
		return self.db.child('member').get().val()

	def get_scheduled_members(self, date):
		if date is None:
			date = ''
		date = str(date)
		return self.db.child('member').order_by_child('scheduled').equal_to(date).get().val()

	def delete_member(self, member):
		_logger.debug("Deleting %s",member)
		self.db.child('member').child(member['ID']).remove()

