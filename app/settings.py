import aioredis

FAVICON_PATH = "app/static/favicon.ico"
REDIS_CONNECTION_STRING = "redis://localhost"

REDIS_CLIENT = aioredis.from_url(REDIS_CONNECTION_STRING)
