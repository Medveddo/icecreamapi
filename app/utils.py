import hashlib
import os
import random
from datetime import datetime
from typing import List, Optional

import requests

from .models import IceCream, Order, OrderPosition, UserIn, UserOut
from .settings import REDIS_CLIENT, SERVER_STATIC_PREFIX, STATIC_FOLDER_PATH


class HashUtils:  # pragma: no cover
    @staticmethod
    def get_sha256_hash(input: str) -> bytes:
        hash = hashlib.sha256()
        hash.update(input.encode("utf-8"))
        return hash.digest()

    @staticmethod
    def gen_user_token() -> int:
        return random.randint(1000000000, 2000000000)


class ImageUtils:
    @staticmethod
    def save_icecream_image_to_static(image_url: str, id: int) -> str:
        image = requests.get(image_url)
        file_extension = os.path.splitext(image_url)[-1]
        if not file_extension:
            file_extension = ".jpg"
        file_name = f"icecream_{id}{file_extension}"
        file_path = f"{STATIC_FOLDER_PATH}icecream_{id}{file_extension}"
        with open(file_path, "wb") as file:
            file.write(image.content)
        print(f"SAVED {image_url} to {file_path}")
        return f"{SERVER_STATIC_PREFIX}{file_name}"


class RedisUtils:
    @staticmethod
    async def get_new_object_id(object_name: str) -> int:
        id = await REDIS_CLIENT.incr(f"{object_name}_highest_id")
        print(f"INFO: New {object_name} id: {id}")
        return id

    @staticmethod
    async def get_icecream_by_id(id_: int) -> Optional[IceCream]:
        ice_dict: dict = await REDIS_CLIENT.hgetall(f"icecream:{id_}")
        if not ice_dict:
            return None
        return IceCream(
            id=ice_dict[b"id"],
            name=ice_dict[b"name"],
            price=float(ice_dict[b"price"]),
            weight=float(ice_dict[b"weight"]),
            img_url=ice_dict[b"img_url"],
        )

    @staticmethod
    async def get_all_icecream_ids() -> List[int]:
        icecream_ids: List[str] = await REDIS_CLIENT.lrange("icecream_ids", 0, -1)
        return [int(id) for id in icecream_ids]

    @staticmethod
    async def get_all_ice_creams() -> List[IceCream]:
        icecream_ids = await RedisUtils.get_all_icecream_ids()
        icecreams = []
        for id_ in icecream_ids:
            icecreams.append(await RedisUtils.get_icecream_by_id(id_))
        return icecreams

    @staticmethod
    async def get_icecream_count() -> int:
        return await REDIS_CLIENT.llen("icecream_ids")

    @staticmethod
    async def create_ice_cream(icecream: IceCream) -> IceCream:
        icecream.id = await RedisUtils.get_new_object_id("icecream")
        icecream.img_url = ImageUtils.save_icecream_image_to_static(
            icecream.img_url, icecream.id
        )
        await REDIS_CLIENT.rpush("icecream_ids", icecream.id)
        await REDIS_CLIENT.hset(f"icecream:{icecream.id}", mapping=icecream.dict())
        print(f"INFO: Icecream created ({icecream})")
        return icecream

    @staticmethod
    async def create_user(user: UserIn) -> Optional[UserOut]:
        password_hash = HashUtils.get_sha256_hash(user.password)
        await REDIS_CLIENT.hset(f"user:{user.login}", "hash", password_hash)
        print(f"INFO: User created ({user.login})")
        return UserOut(login=user.login, created_at=datetime.now())

    @staticmethod
    async def is_user_exist(login: str) -> bool:
        return bool(await REDIS_CLIENT.exists(f"user:{login}"))

    @staticmethod
    async def user_has_valid_password(user: UserIn) -> bool:
        redis_user = await REDIS_CLIENT.hgetall(f"user:{user.login}")
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

        await REDIS_CLIENT.hset(f"order:{order_id}", "order", order.json())
        await REDIS_CLIENT.rpush(f"user:{user_login}:orders", order_id)
        await REDIS_CLIENT.rpush("order_ids", order_id)

        print(f"INFO: Order created ({order})")
        return order

    @staticmethod
    async def get_user_orders(user_login: str) -> List[Order]:
        orders: List[Order] = []
        for id_ in await RedisUtils.get_user_orders_ids(user_login):
            order_raw = await REDIS_CLIENT.hget(f"order:{id_}", "order")
            orders.append(Order.parse_raw(order_raw))
        return orders

    async def get_user_orders_ids(user_login: str) -> List[int]:
        ids = await REDIS_CLIENT.lrange(f"user:{user_login}:orders", 0, 1)
        return [int(id_) for id_ in ids]
