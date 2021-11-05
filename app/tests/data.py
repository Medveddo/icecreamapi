import fakeredis.aioredis
from fastapi.testclient import TestClient

from ..main import app

ICECREAM_IDS = [1, 5, 6]

client = TestClient(app)

global_fake_redis = fakeredis.aioredis.FakeRedis()
