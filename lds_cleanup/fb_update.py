import requests

from .database import Database
from .log import logging
_logger = logging.getLogger('lds_cleanup.fb_update')

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

    res = {}
    for mem in fb_data:
        name =mem['name'].split(' ')
        name = name[0] + ' ' + name[-1]
        res[name]=mem['id']
    return res

def update_member_fb_data():
    fb_data = get_fb_group_members()
    mem_count = len(fb_data)

    db = Database()
    db.add_fb_count(mem_count)

    count = 0
    members = db.get_all_members()
    for mem in members.values():
        # print(mem)
        name = mem['name'].split(' ')[0] + ' ' + mem['surname']
        try:
            data = {'fbid':fb_data[name], 'ID':mem['ID']}
            db.save_member(data)
            count += 1
            _logger.info("Adding FB ID for {}".format(name))
        except KeyError:
            surname = mem['surname']
            for prof_name in fb_data.keys():
                if surname.lower() in prof_name.lower():
                    print("Trying {} = {}".format(prof_name, name))
                    if name[:3].lower() in prof_name.split(' ')[0].lower():
                        ans = input('{} = {}? '.format(prof_name, name))
                        if ans == '' or ans == 'y':
                            data = {'fbid':fb_data[prof_name], 'ID':mem['ID']}
                            db.save_member(data)
                            count += 1
                            break
    db.add_fb_active_count(count)
    _logger.info("{} of {} fb members are actual members".format(count, mem_count))

if __name__ == '__main__':
    update_member_fb_data()

