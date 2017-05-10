from database import Database 
from phone_api import Phone, compare_numbers
from log import logging
_logger = logging.getLogger('lds_cleanup.phone_api')
phn = Phone()
db = Database()

from flask import Flask, request, redirect, session
import re

# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'
app = Flask(__name__)
app.config.from_object(__name__)

def handle_admin(body):
    m = re.match(r'([\w\s]+):(.*)',body)
    if m is None:
        phn.text("!Error Processing!-{}".format(body))
    name = m.group(1)
    body = m.group(2)
    name_list = name.split(' ')
    surname = name_list[-1]
    name = name_list[0]
    member = db.get_member_by_name(name,str(surname))
    if member is None:
        phn.text("!Error Processing!-{} {}".format(name,surname))
    phn.text(body,to=member['phone'])

def handle_member(member, body):
    phn.text("{name} {surname}: {body}".format(name=member['name'],surname=member['surname'],body=body))


@app.route("/", methods=['GET', 'POST'])
def recv_text():
    from_num = request.values.get('From', None)
    body = request.values.get('Body', None)
    mID = request.values.get('MessageSid', None)
    member = db.get_member_by_phone_number(from_num)

    _logger.info("mID: {mID}, Received a message from {name} {surname} at {phone}:\n{body}".format(mID=mID,name=member['name'],surname=member['surname'],phone=member['phone'],body=body))

    if compare_numbers(from_num, phn.admin_number):
        handle_admin(body)
    else:
        handle_member(member,body)

    return r'<?xml version="1.0" encoding="UTF-8"?><Response />'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8992)