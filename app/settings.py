import aioredis

FAVICON_PATH = "app/static/favicon.ico"
REDIS_CONNECTION_STRING = "redis://localhost"

MAIN_PAGE_RESPONSE = "✨ Main page! ✨ 🔥GitHub actions top!🔥"

REDIS_CLIENT = aioredis.from_url(REDIS_CONNECTION_STRING)
