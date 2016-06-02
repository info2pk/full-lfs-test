# -*- coding: utf-8 -*-
import logging
import pylibmc
from . import (Lock, HOST_IDENTIFIER,
               LOCK_TIME, INITIAL_LOCK_TIME, HEARTBEAT_INTERVAL)

logger = logging.getLogger(__name__)


class MemcachedLock(Lock):
    def __init__(self, server_uri, *args):
        self.lock_time = int(LOCK_TIME or 1)
        self.initial_lock_time = int(INITIAL_LOCK_TIME or (self.lock_time * 2))
        self.heartbeat_interval = int(HEARTBEAT_INTERVAL or 1)
        self.server_uri = server_uri.split(',')

        self.mc = pylibmc.Client(self.server_uri)
        logger.debug('MemcacheLock init. lock_time={}, heartbeat_interval={}, server_uri={}'.format(
            self.lock_time, self.heartbeat_interval, self.server_uri))

    def acquire_lock(self):
        value = "%s:%s" % (HOST_IDENTIFIER, '0')
        logger.debug('MemcacheLock acquire lock. {}={}'.format(self.lock_key, value))
        return self.mc.add(self.lock_key, value, time=self.initial_lock_time)

    def refresh_lock(self, pid):
        value = "%s:%s" % (HOST_IDENTIFIER, pid)
        self.mc.set(self.lock_key, value, time=LOCK_TIME)
        return True
