import socket
import os
import sys

LOCK = None

ARGS = sys.argv[1:]
IDENTIFIER = os.environ.get('SINGLE_BEAT_IDENTIFIER') or (ARGS[0] if ARGS else None)
HOST_IDENTIFIER = os.environ.get('SINGLE_BEAT_HOST_IDENTIFIER',
                                 socket.gethostname())

LOCK_TIME = int(os.environ.get('SINGLE_BEAT_LOCK_TIME', 5))
INITIAL_LOCK_TIME = int(os.environ.get('SINGLE_BEAT_INITIAL_LOCK_TIME',
                                       LOCK_TIME * 2))
HEARTBEAT_INTERVAL = int(os.environ.get('SINGLE_BEAT_HEARTBEAT_INTERVAL', 1))

MEMCACHED_SERVERS = os.environ.get('SINGLE_BEAT_MEMCACHED_SERVER')
REDIS_SERVER = os.environ.get('SINGLE_BEAT_REDIS_SERVER')


class Lock(object):

    @property
    def lock_key(self):
        return 'SINGLE_BEAT_%s' % getattr(self, 'identifier', None) or IDENTIFIER

    def acquire_lock(self):
        raise NotImplementedError

    def refresh_lock(self, pid):
        raise NotImplementedError


if REDIS_SERVER:
    from .redis import RedisLock
    LOCK = RedisLock(REDIS_SERVER)
elif MEMCACHED_SERVERS:
    from .memcached import MemcachedLock
    LOCK = MemcachedLock(MEMCACHED_SERVERS)
else:
    raise RuntimeError("No locking backend found. Please choose one.")
