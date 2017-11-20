import requests
from collections import defaultdict

from .database import Database
from .log import logging
_logger = logging.getLogger('lds_robocalling.utils.fb_update')

req = {
    'base_url' : 'https://graph.facebook.com/v2.9',
    'group_id' : '219397588081282', #Ann Arbor YSA ID
    'query' : 'members?limit=500&pretty=0',
    'token' : 'EAACEdEose0cBALDsPhN6DurCaOIEezKywN5nI6ZBaNBTbmXpzp5hLOQBcCEJtqvzEQVTH0DWZCfQ24NdJ4ve3Gs8qtnA8fyEi47CSQoRKmyGZCU1TkbZBfZBP8yjp7QX0FnxjSiy2YgrOlQ8zWQhzzZAIbfw1kHpteIQivclsMMhWixSibZBtFu7XWZB8Yd9bWEZD'
}

def get_fb_group_members():
    try:
        fb_data = requests.get("{base_url}/{group_id}/{query}&access_token={token}".format(**req)).json()['data']
    except KeyError as e:
        raise Exception("Update Your Facebook Token")

    res = defaultdict({})
    for mem in fb_data:
        name =mem['name'].split(' ')
        name = name[0]
        surname =  name[-1]

        res[surname][name]=mem['id']
    return res

