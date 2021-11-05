from unittest.mock import MagicMock, patch

import pytest

from .data import ICECREAM_IDS, global_fake_redis
from ..models import IceCream
from ..utils import RedisUtils


@pytest.fixture()
async def one_icecream_fixture() -> IceCream:
    # @pytest.fixture must be most inner decorator to fixture to yield value, but not async_generator object.
    # and i moved patch'es inside function, maybe I'll try to find a better solution later... maybe...
    # https://pythonrepo.com/repo/pytest-dev-pytest-asyncio-python-testing-codebases-and-generating-test-data#async-fixtures
    with patch("app.utils.REDIS_CLIENT", global_fake_redis), patch(
        "app.utils.ImageUtils.save_icecream_image_to_static",
        MagicMock(return_value="saved_file.jppg"),
    ):
        print("SETUP:one_icecream_fixture")
        ice_cream = IceCream(
            name="ice_cream_1",
            price=10,
            weight=10,
            img_url="http://1.2.3.4/ice_image.jpg",
        )
        icecream = await RedisUtils.create_ice_cream(ice_cream)
        yield icecream
        print("TEARDOWN:one_icecream_fixture")
        await global_fake_redis.flushall()


@pytest.fixture()
@pytest.mark.asyncio
async def icecream_ids_fixture() -> None:
    print("SETUP:icecream_ids_fixture")
    await global_fake_redis.rpush("icecream_ids", *ICECREAM_IDS)
    yield
    print("TEARDOWN:icecream_ids_fixture")
    await global_fake_redis.delete("icecream_ids")
