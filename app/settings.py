import os

import aioredis

FAVICON_PATH = "app/static/favicon.ico"
MAIN_PAGE_RESPONSE = """
    ✨ Main page! ✨ <br>
    🔥 GitHub actions top! 🔥 <br>
    <strong>Total icecreams: {counter}</strong> <br>
    <h2><a href="/docs">Docs</a></h2>
    """
WINDOWS_PLATFORM = False
HOST = "localhost" if os.getenv("LOCAL_DEV") else "217.71.129.139:4561"
SERVER_STATIC_PREFIX = f"http://{HOST}/static/"
STATIC_FOLDER_PATH = "/root/icecreamapi-app/icecreamapi/static/"
REDIS_CONNECTION_STRING = os.getenv("REDIS_URL", "redis://localhost")
REDIS_CLIENT = aioredis.from_url(REDIS_CONNECTION_STRING)
