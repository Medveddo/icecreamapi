from unittest.mock import MagicMock, patch

import fakeredis.aioredis
import pytest

from .data import ICECREAM_IDS, client, global_fake_redis
from ..models import IceCream, Order, OrderPosition, UserIn
from ..utils import RedisUtils


@patch("app.utils.REDIS_CLIENT", global_fake_redis)
@pytest.mark.asyncio
async def test_get_icecreams(one_icecream_fixture: IceCream):
    response = client.get("/api/icecream")
    assert response.status_code == 200
    print(one_icecream_fixture)
    assert one_icecream_fixture.json().replace(" ", "") == response.content.decode(
        "utf-8"
    ).strip("[").strip("]")


@patch("app.utils.REDIS_CLIENT", global_fake_redis)
@pytest.mark.asyncio
async def test_get_all_icecream_ids(icecream_ids_fixture: None):
    assert await RedisUtils.get_all_icecream_ids() == ICECREAM_IDS


@pytest.mark.asyncio
@patch("app.utils.REDIS_CLIENT", fakeredis.aioredis.FakeRedis())
@patch(
    "app.utils.ImageUtils.save_icecream_image_to_static",
    return_value="cool_icecream_image.png",
)
async def test_create_ice_cream(save_icecream_mock: MagicMock):
    icecream = IceCream(
        name="cool icecream",
        price=5.55,
        weight=70,
        img_url="http://imagehouse.space/static/cool_icecream_image.png",
    )
    await RedisUtils.create_ice_cream(icecream)
    assert await RedisUtils.get_icecream_count() == 1
    assert [icecream.id] == await RedisUtils.get_all_icecream_ids()
    print("GOT", await RedisUtils.get_icecream_by_id(1))
    assert await RedisUtils.get_icecream_by_id(1) == icecream
    await global_fake_redis.flushall()


@pytest.mark.asyncio
@patch("app.utils.REDIS_CLIENT", fakeredis.aioredis.FakeRedis())
async def test_get_icecream_by_id_none():
    assert await RedisUtils.get_icecream_by_id(10) is None


@pytest.mark.asyncio
@patch("app.utils.REDIS_CLIENT", global_fake_redis)
async def test_create_user():
    user = UserIn(login="admin", password="bestboss")
    result = await RedisUtils.create_user(user)
    assert result.login == user.login
    assert await global_fake_redis.exists(f"user:{user.login}")
    await global_fake_redis.flushall()


@pytest.mark.asyncio
@patch("app.utils.REDIS_CLIENT", fakeredis.aioredis.FakeRedis())
async def test_is_user_exist():
    login = "user1"
    await RedisUtils.create_user(UserIn(login=login, password="pass1"))
    assert await RedisUtils.is_user_exist(login)
    assert not await RedisUtils.is_user_exist("login_not_exist")


@pytest.mark.asyncio
@patch("app.utils.REDIS_CLIENT", fakeredis.aioredis.FakeRedis())
async def test_user_has_valid_password():
    user = UserIn(login="user1", password="pass1")
    await RedisUtils.create_user(user)
    assert await RedisUtils.user_has_valid_password(user)


@pytest.mark.asyncio
@patch("app.utils.REDIS_CLIENT", fakeredis.aioredis.FakeRedis())
async def test_create_order():
    user_login = "user1"
    position = OrderPosition(icecream_id=1, quantity=2)
    positions = [position]
    await RedisUtils.create_order(user_login, positions)
    assert await RedisUtils.get_user_orders_ids(user_login) == [1]
    order: Order = (await RedisUtils.get_user_orders(user_login))[0]
    assert order.user_login == user_login
    assert order.id == 1
    assert order.positions[0] == position
