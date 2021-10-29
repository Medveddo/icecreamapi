from datetime import datetime
from typing import List
from .settings import REDIS_CLIENT
from .models import IceCream, UserIn, UserOut
import hashlib


class HashUtils:
    @staticmethod
    def get_sha256_hash(input: str) -> bytes:
        hash = hashlib.sha256()
        hash.update(input.encode("utf-8"))
        return hash.digest()


class RedisUtils:
    @staticmethod
    async def get_new_object_id(object_name: str) -> int:
        id = await REDIS_CLIENT.incr(f"{object_name}_highest_id")
        print(f"INFO: New {object_name} id: {id}")
        return id

    @staticmethod
    async def save_ice_cream(icecream: IceCream) -> None:
        json_icecream = icecream.json()
        await REDIS_CLIENT.lpush("icecreams", json_icecream)
        print(f"INFO: Saved {icecream} to storage")

    @staticmethod
    async def get_all_ice_creams() -> List["IceCream"]:
        result = []
        raw_icecreams = await REDIS_CLIENT.lrange("icecreams", 0, -1)
        for raw in raw_icecreams:
            result.append(IceCream.parse_raw(raw))
        return result

    @staticmethod
    async def create_user(user: UserIn) -> UserOut:
        password_hash = HashUtils.get_sha256_hash(user.password)

        # TODO: check if exist
        await REDIS_CLIENT.hset(f"users:{user.login}", "hash", password_hash)
        print(f"INFO: Saved {user.login} to storage")
        user_out = UserOut(login=user.login, creation_date=datetime.now())
        return user_out

    @staticmethod
    async def is_user_exist(login: str) -> bool:
        return bool(await REDIS_CLIENT.hgetall(f"users:{login}"))

    @staticmethod
    async def user_has_valid_password(user: UserIn) -> bool:
        redis_user = await REDIS_CLIENT.hgetall(f"users:{user.login}")
        password_hash = HashUtils.get_sha256_hash(user.password)
        return redis_user[b"hash"] == password_hash
