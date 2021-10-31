import hashlib
import random
from datetime import datetime
from typing import List, Optional

from .models import IceCream, Order, OrderPosition, UserIn, UserOut
from .settings import REDIS_CLIENT


class HashUtils:
    @staticmethod
    def get_sha256_hash(input: str) -> bytes:
        hash = hashlib.sha256()
        hash.update(input.encode("utf-8"))
        return hash.digest()

    @staticmethod
    def gen_user_token() -> int:
        return random.randint(1000000000, 2000000000)


class RedisUtils:
    @staticmethod
    async def get_new_object_id(object_name: str) -> int:
        id = await REDIS_CLIENT.incr(f"{object_name}_highest_id")
        print(f"INFO: New {object_name} id: {id}")
        return id

    @staticmethod
    async def get_ice_cream_by_id(id_: int) -> Optional[IceCream]:
        ice_creams = await RedisUtils.get_all_ice_creams()
        for ice_cream in ice_creams:
            if ice_cream.id == id_:
                return ice_cream
        return None

    @staticmethod
    async def get_all_ice_creams() -> List[IceCream]:
        raw_icecreams = await REDIS_CLIENT.lrange("icecreams", 0, -1)
        return [IceCream.parse_raw(raw) for raw in raw_icecreams][::-1]

    @staticmethod
    async def get_icecream_count() -> int:
        return await REDIS_CLIENT.llen("icecreams")

    @staticmethod
    async def create_ice_cream(icecream: IceCream) -> IceCream:
        icecream.id = await RedisUtils.get_new_object_id("icecream")
        await REDIS_CLIENT.lpush("icecreams", icecream.json())
        print(f"INFO: Icecream created ({icecream})")
        return icecream

    @staticmethod
    async def create_user(user: UserIn) -> Optional[UserOut]:
        password_hash = HashUtils.get_sha256_hash(user.password)
        await REDIS_CLIENT.hset(f"users:{user.login}", "hash", password_hash)
        print(f"INFO: User created ({user.login})")
        return UserOut(login=user.login, creation_date=datetime.now())

    @staticmethod
    async def is_user_exist(login: str) -> bool:
        return bool(await REDIS_CLIENT.hgetall(f"users:{login}"))

    @staticmethod
    async def user_has_valid_password(user: UserIn) -> bool:
        redis_user = await REDIS_CLIENT.hgetall(f"users:{user.login}")
        password_hash = HashUtils.get_sha256_hash(user.password)
        return redis_user[b"hash"] == password_hash

    @staticmethod
    async def create_order(user_login: str, positions: List[OrderPosition]) -> Order:
        order_id = await RedisUtils.get_new_object_id("order")
        order = Order(
            id=order_id,
            user_login=user_login,
            created_at=datetime.now(),
            positions=positions,
        )
        await REDIS_CLIENT.lpush(f"orders:{user_login}", order.json())
        print(f"INFO: Order created ({order})")
        return order

    @staticmethod
    async def get_user_orders(user_login: str) -> List[Order]:
        raw_orders = await REDIS_CLIENT.lrange(f"orders:{user_login}", 0, -1)
        return [Order.parse_raw(raw_order) for raw_order in raw_orders][::-1]
