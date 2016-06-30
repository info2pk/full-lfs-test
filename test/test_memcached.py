import unittest
from mockcache import Client
from singlebeat.locks import LOCK,HOST_IDENTIFIER,MemcachedLock

class MemcachedTestCase(unittest.TestCase):

	def setUp(self):
		self.mc = Client()
		LOCK.identifier = "SINGLE_BEAT_MEMCACHED_SERVER"
		LOCK.mc = self.mc

	def test_acquire_lock(self):
		LOCK.acquire_lock()
		value = "%s:%s" % (HOST_IDENTIFIER, '0')
		self.assertEqual(self.mc.get(LOCK.lock_key),value)

	def test_refreshlock(self):
		LOCK.refresh_lock(777)
		value = "%s:%s" % (HOST_IDENTIFIER, 777)
		self.assertEqual(self.mc.get(LOCK.lock_key),value)


if __name__ == '__main__':
    unittest.main()