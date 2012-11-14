'''
This is a helper from https://gist.github.com/609238 that opens and closes
connections to Redis. Problem is that a single request might involve hundreds
of connections, which is overhead. Similarly, we can just keep a persistent
connection open. So, we open a connection for each request, then close
it when the request stops.

'''


import redis
import uuid
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
    
    _increment_stats('redis_hits')
    
    if r_server.exists(key):
        if lookup == False:
            return True
        else:
            return r_server.hgetall(key)
    
    else:
        return None


def _add_to_redis(key, values, user=None):

    #mapping = MAPPING_CHINESE_WORD
    #for k, v in mapping.iteritems():
    #    try:
    #        mapping[k] = values[k]
    #    except KeyError:
    #        raise KeyError('Some kind of problem in _add_to_redis in redis_helper.py adding the values onto the mapping provided')
        

    r_server = _get_redis()
    if r_server.exists(key):
        if user:
            
            if user.is_authenticated() and str(user.email) in key:
                r_server.hmset(key, values)
            else:
                print "hmm, no user in the key - passing overwrite"
                pass

        # for the moment, we'll pass. Later, we'll meed to decide on 
        # some kind of overwrite permissions or notifications.
                
    else:
        
        r_server.hmset(key, values)
        
    return True


def _increment_stats(metric):
    r_server = _get_redis()
    key = "stats:%s:%s" % (datetime.date.today().year, datetime.date.today().month)  

    if r_server.exists(key):
        r_server.hincrby(key, metric, 1)
    else:
        mapping = {
                     'searches': 1,
                     'redis_hits': 1,   
                }
                
        _add_to_redis(key, values)
    
    return True    
  

    