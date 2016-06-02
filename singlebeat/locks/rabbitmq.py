# -*- coding: utf-8 -*-
import pika
from singlebeat.locks import (Lock, IDENTIFIER, HOST_IDENTIFIER,
                              LOCK_TIME, INITIAL_LOCK_TIME, HEARTBEAT_INTERVAL)


class RabbitMQLock(Lock):

    def __init__(self, server_uri):
        self.identifier = IDENTIFIER
        self.lock_time = int(LOCK_TIME or 12)
        self.initial_lock_time = int(INITIAL_LOCK_TIME or (self.lock_time * 2))
        self.heartbeat_interval = int(HEARTBEAT_INTERVAL or 4)
        self.server_uri = server_uri
        self.args = {'x-message-ttl': self.lock_time * 100}

        parameters = pika.URLParameters(self.server_uri)
        self.exchange = 'single-beat'
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, type='fanout')
        self.q = self.channel.queue_declare(exclusive=True, arguments=self.args)
        self.queue_name = self.q.method.queue
        self.channel.queue_bind(exchange=self.exchange,
                                queue=self.queue_name,
                                routing_key=self.lock_key)

    def acquire_lock(self):
        from time import sleep
        sleep(self.heartbeat_interval)
        method_frame, header_frame, body = self.channel.basic_get(self.queue_name)
        if not body:
            value = "%s:%s" % (HOST_IDENTIFIER, '0')
            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=self.lock_key,
                                       body=value)
            return True
        self.channel.queue_purge(self.queue_name)
        return False

    def refresh_lock(self, pid):
        value = "%s:%s" % (HOST_IDENTIFIER, pid)
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=self.lock_key,
                                   body=value)
        return True
