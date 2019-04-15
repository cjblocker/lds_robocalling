import requests
from collections import defaultdict
import logging
_logger = logging.getLogger('lds_robocalling.services.fb_update')

FB_API_BASE = 'https://graph.facebook.com/v2.9'

def get_fb_group_members(group_id, token, limit=500):
    query = f'members?limit={limit}&pretty=0&access_token={token}'
    try:
        fb_data = requests.get(f"{FB_API_BASE}/{group_id}/{query}").json()['data']
    except KeyError as e:
        raise Exception("Update Your Facebook Token")

    res = defaultdict({})
    for mem in fb_data:
        name =mem['name'].split(' ')
        name = name[0]
        surname =  name[-1]

        res[surname][name]=mem['id']
    return res

