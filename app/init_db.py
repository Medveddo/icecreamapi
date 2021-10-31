import asyncio
import json

from .models import IceCream, UserIn
from .settings import WINDOWS_PLATFORM
from .utils import RedisUtils


async def get_file_dict() -> dict:
    with open("ice.json", "r") as file:
        return json.loads(file.read())


async def load_data_from_file():
    data = await get_file_dict()
    for user in data["users"]:
        await RedisUtils.create_user(UserIn(**user))

    for icecream in data["icecreams"]:
        await RedisUtils.create_ice_cream(IceCream(**icecream))

    await asyncio.sleep(1)


if __name__ == "__main__":
    if WINDOWS_PLATFORM:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(load_data_from_file())
