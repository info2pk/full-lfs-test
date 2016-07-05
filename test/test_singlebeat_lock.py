# -*- coding: utf-8 -*-
import signal
import pyuv
import sys
import unittest
import singlebeat.beat
import subprocess
import os
from singlebeat.locks import LOCK

class SingleBeatValidateLockTestCase(unittest.TestCase):

    ARGS = ["single-beat-test","/home/<USER>/.virtualenvs/singlebeat/bin/single-beat","/home/<USER>/.virtualenvs/singlebeat/bin/celery","beat","--loglevel=DEBUG"]

    def setUp(self):
        self.instance1 = singlebeat.beat.Process(sys.argv)
        self.instance2 = singlebeat.beat.Process(sys.argv)
        self.testResult = False

    def tearDown(self):
        p = subprocess.Popen(['pgrep', '-l' , 'single-beat'], stdout=subprocess.PIPE)
        out, err = p.communicate()

        for line in out.splitlines():        
            line = bytes.decode(line)
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)

    def test_lock(self):
        self.assertTrue(self.validate_instance_lock(self.ARGS), msg=None)

    def validate_instance_lock(self,ARGS):
        sys.argv = ARGS
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(2)
        try:
            self.instance1.timer.start(self.instance1.timer_cb, 0.1, LOCK.heartbeat_interval)
            self.instance1.loop.run()
            signal.alarm(0)
        except Exception as e:
            print e
        return self.testResult

    def timeout_handler2(self,signum, frame):   # Custom signal handler
        print "State instance 1: "+self.instance1.state
        print "State instance 2: "+self.instance2.state
        self.testResult = (self.instance1.state == "RUNNING" and self.instance2.state == "WAITING")
        self.instance1.loop.stop()
        self.instance2.loop.stop()

    def timeout_handler(self,signum, frame):   # Custom signal handler
        try:
            signal.signal(signal.SIGALRM, self.timeout_handler2)
            signal.alarm(1)
            self.instance2.timer.start(self.instance2.timer_cb, 0.1, LOCK.heartbeat_interval)
            self.instance2.loop.run(pyuv.UV_RUN_ONCE)
        except Exception as e:
            print e

if __name__ == '__main__':
    unittest.main()
