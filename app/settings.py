import os

import aioredis

from .service_utils import ServiceUtils

FAVICON_PATH = "app/static/favicon.ico"
REDIS_CONNECTION_STRING = os.getenv("REDIS_URL", "redis://localhost")


MAIN_PAGE_RESPONSE = """
    ✨ Main page! ✨ <br>
    🔥 GitHub actions top! 🔥 <br>
    <strong>Total icecreams: {counter}</strong> <br>
    <h2><a href="/docs">Docs</a></h2>
    """
WINDOWS_PLATFORM = False
SERVER_STATIC_PREFIX = "http://217.71.129.139:4561/static/"
STATIC_FOLDER_PATH = ServiceUtils().get_static_path()
REDIS_CLIENT = aioredis.from_url(REDIS_CONNECTION_STRING)
