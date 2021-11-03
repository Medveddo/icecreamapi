from unittest.mock import MagicMock, patch

import fakeredis.aioredis
from fastapi.testclient import TestClient
import pytest

from .main import app
from .models import IceCream
from .utils import RedisUtils

client = TestClient(app)

global_fake_redis = fakeredis.aioredis.FakeRedis()


@pytest.fixture()
@pytest.mark.asyncio
@patch("app.utils.REDIS_CLIENT", global_fake_redis)
@patch(
    "app.utils.ImageUtils.save_icecream_image_to_static", return_value="saved_file.jppg"
)
async def one_icecream_fixture(save_ice_mock: MagicMock) -> IceCream:
    ice_cream = IceCream(
        name="ice_cream_1", price=10, weigth=10, img_url="http://1.2.3.4/ice_image.jpg"
    )
    return await RedisUtils.create_ice_cream(ice_cream)


@patch("app.utils.REDIS_CLIENT", global_fake_redis)
@pytest.mark.asyncio
async def test_read_main(one_icecream_fixture: IceCream):
    response = client.get("/api/icecream")
    assert response.status_code == 200
    assert one_icecream_fixture.json().replace(" ", "") == response.content.decode(
        "utf-8"
    ).strip("[").strip("]")
