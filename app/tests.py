import unittest
from unittest.mock import patch

import fakeredis.aioredis

from .utils import RedisUtils


class TestRedisUtils(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.redis = fakeredis.aioredis.FakeRedis()

    async def asyncTearDown(self):
        await self.redis.close()

    async def test_connection(self):
        assert await self.redis.incr("health") == 1

    async def test_get_new_object_id(self):
        with patch("app.utils.REDIS_CLIENT", self.redis):
            assert await RedisUtils.get_new_object_id("apple") == 1
            assert await RedisUtils.get_new_object_id("apple") == 2
            assert await RedisUtils.get_new_object_id("user") == 1
