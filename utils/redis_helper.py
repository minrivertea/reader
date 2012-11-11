'''
This is a helper from https://gist.github.com/609238 that opens and closes
connections to Redis. Problem is that a single request might involve hundreds
of connections, which is overhead. Similarly, we can just keep a persistent
connection open. So, we open a connection for each request, then close
it when the request stops.

'''


import redis

from django.conf import settings
from django.core.signals import request_finished
import datetime

try:
    from eventlet.corolocal import local
except ImportError:
    from threading import local

REDIS_HOST = getattr(settings, 'REDIS_HOST', '127.0.0.1')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)
REDIS_DB = getattr(settings, 'REDIS_DB', 8)

REDIS_LOCAL = local()

def _get_redis():
    try:
        return REDIS_LOCAL.client
    except AttributeError:
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        REDIS_LOCAL.client = client
        return client

def cleanup(sender, **kwargs):
    try:
        client = REDIS_LOCAL.client
        del REDIS_LOCAL.client
    except AttributeError:
        return
    try:
        client.disconnect()
    except (KeyboardInterrupt, SystemExit, MemoryError):
        raise
    except:
        pass

request_finished.connect(cleanup)



"""
THE FOLLOWING stuff is custom written by Chris West and manages all our 
dictionary adding/searching type things. Helps to keep this information
here so that it's nicely organised.

"""


def _search_redis(key, lookup=True):
    r_server = _get_redis()
    
    stats_key = "stats:%s:%s" % (datetime.date.today().year, datetime.date.today().month)    
    if r_server.exists(key):
        r_server.hincrby(stats_key, 'redis_hits', 1)
        if lookup == False:
            return True
        else:
            return r_server.hgetall(key)
    
    else:
        return None


def _add_to_redis(key, values):

    
    r_server = _get_redis()
    if r_server.exists(key):
        object = search_redis(key)
        count = (int(object['count']) + 1)
        new1 = "meaning%s" % count
        new2 = "pinyin%s" % count
        
        mapping = {
            new1: values['meaning'],
            new2: values['pinyin'], 
            'count': count,
        }
        
        r_server.hmset(key, mapping)
                
    else:
        mapping = {
            'chars': values['characters'],
            'pinyin1': values['pinyin'], 
            'meaning1': values['meaning'],
            'count': 1,
            'id': uuid.uuid4().hex,
        }
        
        r_server.hmset(key, mapping)
        
    return True