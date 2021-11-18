from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import FileResponse, HTMLResponse, Response

from .models import (
    IceCream,
    Order,
    OrderPosition,
    ResponceDetail,
    SuccessToken,
    UserIn,
    UserOut,
)
from .settings import FAVICON_PATH, MAIN_PAGE_RESPONSE
from .utils import HashUtils, RedisUtils

router = APIRouter()
security = HTTPBasic()


@router.get(
    path="/error",
    tags=["service"],
    summary="Always unavailable",
    responses={
        503: {
            "content": {
                "application/json": {"example": [{"detail": "service is unavailable"}]}
            }
        }
    },
)
async def service_unavailable():
    raise HTTPException(503, detail="service is unavailable")


@router.get("/", response_class=HTMLResponse)
async def root():
    return MAIN_PAGE_RESPONSE.format(counter=await RedisUtils.get_icecream_count())


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(FAVICON_PATH)


@router.get(
    "/api/icecream/",
    tags=["icecream"],
    summary="Get all icecreams",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "Hot Summer",
                            "price": 15.89,
                            "weight": 70.0,
                            "img_url": "https://media-cdn.tripadvisor.com/media/photo-s/18/7c/da/68/bonmot-ice-cream.jpg",
                        },
                        {
                            "id": 2,
                            "name": "Blue Water",
                            "price": 13.56,
                            "weight": 50.0,
                            "img_url": "https://media-cdn.tripadvisor.com/media/photo-s/18/7c/da/68/bonmot-ice-cream.jpg",
                        },
                    ]
                }
            },
        }
    },
)
async def get_icecreams() -> List[IceCream]:
    return await RedisUtils.get_all_ice_creams()


@router.get(
    path="/api/icecream/{item_id}",
    tags=["icecream"],
    summary="Get ice cream by id",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "Hot Summer",
                            "price": 15.89,
                            "weight": 70.0,
                            "img_url": "https://media-cdn.tripadvisor.com/media/photo-s/18/7c/da/68/bonmot-ice-cream.jpg",
                        }
                    ]
                }
            },
        },
        404: {
            "content": {"application/json": {"example": [{"detail": "not found"}]}},
        },
    },
)
async def get_icecream_by_id(item_id: int) -> IceCream:
    ice_cream = await RedisUtils.get_icecream_by_id(item_id)
    if not ice_cream:
        raise HTTPException(status_code=404, detail="not found")
    return ice_cream


@router.post(
    "/api/icecream/", tags=["icecream"], summary="Add new icecream", status_code=201
)
async def create_item(ice_cream: IceCream):
    return await RedisUtils.create_ice_cream(ice_cream)


@router.post(
    path="/api/user/new",
    summary="Create user",
    tags=["users"],
    status_code=201,
    responses={
        201: {
            "description": "User created",
            "content": {
                "application/json": {
                    "example": {
                        "login": "bestboss",
                        "created_at": datetime(2021, 10, 23, 12, 56),
                    }
                }
            },
        },
        409: {
            "model": ResponceDetail,
            "description": "User already exist",
            "content": {
                "application/json": {
                    "example": {"detail": "user with this login already exist"}
                }
            },
        },
    },
)
async def new_user(user_in: UserIn) -> UserOut:
    if await RedisUtils.is_user_exist(user_in.login):
        raise HTTPException(
            status_code=409, detail="user with this login already exists"
        )
    return await RedisUtils.create_user(user_in)


@router.post(
    path="/api/user/login",
    summary="Login using basic auth",
    tags=["users"],
    responses={
        200: {
            "model": SuccessToken,
            "description": "Successfull login",
            "content": {"application/json": {"example": {"token": 1977390630}}},
        },
        401: {
            "model": ResponceDetail,
            "description": "Invalid credentials",
            "content": {
                "application/json": {"example": {"detail": "invalid credentials"}}
            },
        },
        404: {
            "model": ResponceDetail,
            "description": "User not found",
            "content": {"application/json": {"example": {"detail": "user not found"}}},
        },
    },
)
async def login(credentials: HTTPBasicCredentials = Depends(security)) -> SuccessToken:
    user = UserIn(login=credentials.username, password=credentials.password)
    if not await RedisUtils.is_user_exist(credentials.username):
        raise HTTPException(status_code=404, detail="user not found")
    if not await RedisUtils.user_has_valid_password(user):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return {"token": HashUtils.gen_user_token()}


@router.post(
    path="/api/order/new",
    summary="Create order",
    tags=["orders"],
    status_code=201,
    responses={
        201: {
            "model": Order,
            "description": "Order created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_login": "bestboss",
                        "created_at": datetime(2021, 11, 11, 11, 11, 11),
                        "positions": [
                            OrderPosition(icecream_id=1, quantity=2),
                            OrderPosition(icecream_id=2, quantity=3),
                        ],
                    }
                }
            },
        },
        401: {
            "model": ResponceDetail,
            "description": "Invalid credentials",
            "content": {
                "application/json": {"example": {"detail": "invalid credentials"}}
            },
        },
    },
)
async def make_order(
    positions: List[OrderPosition],
    credentials: HTTPBasicCredentials = Depends(security),
) -> Order:
    user = UserIn(login=credentials.username, password=credentials.password)
    if not await RedisUtils.is_user_exist(
        user.login
    ) or not await RedisUtils.user_has_valid_password(user):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return await RedisUtils.create_order(user.login, positions)


@router.get(
    path="/api/order/my",
    summary="Get all user orders",
    tags=["orders"],
    responses={
        200: {
            "model": List[Order],
            "description": "User orders",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "user_login": "bestboss",
                            "created_at": datetime(2021, 11, 11, 11, 11, 11),
                            "positions": [
                                OrderPosition(icecream_id=1, quantity=2),
                                OrderPosition(icecream_id=2, quantity=3),
                            ],
                        },
                        {
                            "id": 2,
                            "user_login": "bestboss",
                            "created_at": datetime(2021, 12, 12, 12, 12, 12),
                            "positions": [
                                OrderPosition(icecream_id=4, quantity=1),
                                OrderPosition(icecream_id=5, quantity=1),
                            ],
                        },
                    ]
                }
            },
        },
        401: {
            "model": ResponceDetail,
            "description": "Invalid credentials",
            "content": {
                "application/json": {"example": {"detail": "invalid credentials"}}
            },
        },
    },
)
async def get_user_orders(
    credentials: HTTPBasicCredentials = Depends(security),
) -> List[Order]:
    user = UserIn(login=credentials.username, password=credentials.password)
    if not await RedisUtils.is_user_exist(
        user.login
    ) or not await RedisUtils.user_has_valid_password(user):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return await RedisUtils.get_user_orders(user.login)


@router.put(
    path="/api/icecream/{item_id}",
    response_model=IceCream,
    status_code=200,
    tags=["icecream"],
    summary="Update icecream",
)
async def update_icecream(item_id: int, icecream: IceCream):
    saved_icecream = await RedisUtils.get_icecream_by_id(item_id)
    if not saved_icecream:
        raise HTTPException(404, f"Icecream with id {item_id} not found")
    update_data = icecream.dict(exclude_unset=True)
    saved_icecream_dict = saved_icecream.dict()
    saved_icecream_dict.update(update_data)
    updated_icecream = IceCream.parse_obj(saved_icecream_dict)
    return await RedisUtils.update_icecream(updated_icecream)



@router.delete(
    path="/api/icecream/{item_id}",
    status_code=204,
    tags=["icecream"],
    summary="Delete icecream"
)
async def delete_icecream(item_id: int):
    icecream = await RedisUtils.get_icecream_by_id(item_id)
    if not icecream:
        raise HTTPException(404, f"Icecream with id {item_id} not found")
    await RedisUtils.delete_icecream(item_id)
    return Response(status_code=204)