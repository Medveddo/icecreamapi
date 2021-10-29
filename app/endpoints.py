from typing import List
from fastapi import Response, status, APIRouter, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime
import random
from starlette.responses import FileResponse
from .settings import FAVICON_PATH

from .models import (
    IceCream,
    Order,
    UserIn,
    UserOut,
    Message,
    SuccessToken,
    OrderPosition,
)
from .settings import REDIS_CLIENT
from .utils import RedisUtils

router = APIRouter()
security = HTTPBasic()


@router.get("/")
async def root():
    print(REDIS_CLIENT)
    return "✨ Main page ✨\n 🔥GitHub actions top!🔥"


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
                            "weigth": 70.0,
                            "img_url": "https://media-cdn.tripadvisor.com/media/photo-s/18/7c/da/68/bonmot-ice-cream.jpg",
                        },
                        {
                            "id": 2,
                            "name": "Blue Water",
                            "price": 13.56,
                            "weigth": 50.0,
                            "img_url": "https://media-cdn.tripadvisor.com/media/photo-s/18/7c/da/68/bonmot-ice-cream.jpg",
                        },
                    ]
                }
            },
        }
    },
)
async def get_icecreams():
    print("INFO:\t GET /api/icecream/")
    icecreams = await IceCream.all()
    return icecreams


@router.post("/api/icecream/", tags=["icecream"], summary="Add new icecream")
async def create_item(ice_cream: IceCream):
    print("INFO:\t POST /api/icecream/")
    ice_cream.id = await RedisUtils.get_new_object_id("icecream")
    await IceCream.save(ice_cream)
    return ice_cream


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
                        "creation_date": datetime(2021, 10, 23, 12, 56),
                    }
                }
            },
        },
        409: {
            "model": Message,
            "description": "User already exist",
            "content": {
                "application/json": {
                    "example": {"message": "user with this login already exist"}
                }
            },
        },
    },
)
async def new_user(user_in: UserIn, responce: Response):
    if await RedisUtils.is_user_exist(user_in.login):
        responce.status_code = status.HTTP_409_CONFLICT
        return {"message": "user with this login already exists"}

    user_out: UserOut = await RedisUtils.create_user(user_in)
    responce.status_code = status.HTTP_201_CREATED
    return user_out


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
            "model": Message,
            "description": "Invalid credentials",
            "content": {
                "application/json": {"example": {"message": "invalid credentials"}}
            },
        },
        404: {
            "model": Message,
            "description": "User not found",
            "content": {"application/json": {"example": {"message": "user not found"}}},
        },
    },
)
async def login(
    responce: Response, credentials: HTTPBasicCredentials = Depends(security)
):
    user = UserIn(login=credentials.username, password=credentials.password)
    if not await RedisUtils.is_user_exist(credentials.username):
        responce.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "user not found"}
    if not await RedisUtils.user_has_valid_password(user):
        responce.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "invalid credentials"}
    responce.status_code = status.HTTP_200_OK
    return {"token": random.randint(1000000000, 2000000000)}


@router.post(
    path="/api/order/new",
    summary="Create order",
    tags=["orders"],
    responses={
        200: {
            "model": Order,
            "description": "Order created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "created_at": datetime(2021, 11, 11, 11, 11, 11),
                    }
                }
            },
        },
    },
)
async def make_order(
    responce: Response,
    positions: List[OrderPosition],
    credentials: HTTPBasicCredentials = Depends(security)
):
    user = UserIn(login=credentials.username, password=credentials.password)
    if not await RedisUtils.is_user_exist(user.login) or not await RedisUtils.user_has_valid_password(user):
        responce.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "invalid credentials"}

    # id = await RedisUtils.get_new_object_id("order")
    for position in positions:
        print(position)
    return positions  # Order(id=id, created_at=datetime.utcnow())
