import os

import aioredis

from fakeredis.aioredis import FakeRedis

FAVICON_PATH = "app/static/favicon.ico"
REDIS_CONNECTION_STRING = os.getenv("REDIS_URL", "redis://localhost")


MAIN_PAGE_RESPONSE = """
    ✨ Main page! ✨ <br>
    🔥 GitHub actions top! 🔥 <br>
    <strong>Total icecreams: {counter}</strong> <br>
    <h2><a href="/docs">Docs</a></h2>
    """
USE_FAKE_REDIS = False
WINDOWS_PLATFORM = False

if USE_FAKE_REDIS:
    REDIS_CLIENT = FakeRedis()
else:
    REDIS_CLIENT = aioredis.from_url(REDIS_CONNECTION_STRING)
