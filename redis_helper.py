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

try:
    from eventlet.corolocal import local
except ImportError:
    from threading import local

REDIS_HOST = getattr(settings, 'REDIS_HOST', '127.0.0.1')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)
REDIS_DB = getattr(settings, 'REDIS_DB', 8)

REDIS_LOCAL = local()

def get_redis():
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