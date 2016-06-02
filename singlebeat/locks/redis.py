# -*- coding: utf-8 -*-
import logging
import redis
from singlebeat.locks import (Lock, HOST_IDENTIFIER,
                              LOCK_TIME, INITIAL_LOCK_TIME, HEARTBEAT_INTERVAL)

logger = logging.getLogger(__name__)


class RedisLock(Lock):
    def __init__(self, server_uri, *args):
        self.lock_time = int(LOCK_TIME or 1)
        self.initial_lock_time = int(INITIAL_LOCK_TIME or (self.lock_time * 2))
        self.heartbeat_interval = int(HEARTBEAT_INTERVAL or 1)
        self.server_uri = server_uri
        self.rds = redis.Redis.from_url(server_uri)
        self.rds.ping()

    def acquire_lock(self):
        value = "%s:%s" % (HOST_IDENTIFIER, '0')
        return self.rds.execute_command('SET', self.lock_key, value, 'NX', 'EX', self.initial_lock_time)

    def refresh_lock(self, pid):
        value = "%s:%s" % (HOST_IDENTIFIER, pid)
        return self.rds.set(self.lock_key, value, ex=self.lock_time)
