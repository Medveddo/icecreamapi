from os import path
from typing import List, Optional
from aioredis.client import Redis
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
import aioredis
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime
import hashlib
import random
from fastapi.responses import JSONResponse
import json


from starlette.responses import FileResponse

redis: Redis = None
favicon_path = "favicon.ico"
app = FastAPI(
    title="IceCreamAPI",
    description="This service is MVP (ultra-minimal 😊) of API for mobile app",
    version="0.0.1",
    contact={
        "name": "Sizikov Vitaly",
        "url": "https://vk.com/vitaliksiz",
        "email": "sizikov.vitaly@gmail.com",
    },
)

# =============
#    Models
# =============


class User(BaseModel):
    login: str
    hash_: bytes


class UserOut(BaseModel):
    login: str
    creation_date: datetime = datetime.now()

    class Config:
        schema_extra = {
            "example": {
                "login": "bestboss",
                "creation_date": datetime(2021, 10, 23, 12, 56),
            }
        }


class UserIn(BaseModel):
    login: str
    password: str

    class Config:
        schema_extra = {"example": {"login": "bestboss", "password": "Pa$$w0rd!"}}

    async def save(user: "UserIn") -> UserOut:
        user.password: str
        bytes_password = user.password.encode("utf-8")
        m = hashlib.sha256()
        m.update(bytes_password)

        # TODO: check if exist
        await redis.hset(f"users:{user.login}", "hash", m.digest())
        print(f"INFO: Saved {user.login} to storage")
        user_out = UserOut(login=user.login, creation_date=datetime.now())
        return user_out


class IceCream(BaseModel):
    id: Optional[int]
    name: str
    price: float
    weigth: float
    img_url: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Hot Summer",
                "img_url": "https://images.google.com/amazing_cat.jpg",
                "price": 35.4,
                "weigth": 50.0,
            }
        }

    async def save(icecream: "IceCream"):
        json_icecream = icecream.json()
        await redis.lpush("icecreams", json_icecream)
        print(f"INFO: Saved {icecream} to storage")

    async def all() -> List["IceCream"]:
        result = []
        raw_icecreams = await redis.lrange("icecreams", 0, -1)
        for raw in raw_icecreams:
            result.append(IceCream.parse_raw(raw))
        return result


class Message(BaseModel):
    message: str


class SuccessToken(BaseModel):
    token: int


# =============
#  END Models
# =============


@app.on_event("startup")
async def startup_event():
    global redis
    app.add_middleware(  # To solve 'WARNING:  Invalid HTTP request received.'
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    redis = aioredis.from_url("redis://localhost")
    await redis.incr("health")
    print("SUCCESS:\tRedis initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()
    print("INFO:\tRedis connection was closed")


async def get_new_icecream_id():
    id = await redis.incr("icecream_highest_id")
    print(f"INFO: New icecream id - {id}")
    return id


# =============
#  Endpoints
# =============


@app.get("/")
async def root():
    return "✨ Main page ✨"


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


@app.get(
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


@app.post("/api/icecream/", tags=["icecream"], summary="Add new icecream")
async def create_item(ice_cream: IceCream):
    print("INFO:\t POST /api/icecream/")
    ice_cream.id = await get_new_icecream_id()
    await IceCream.save(ice_cream)
    return ice_cream


@app.post(
    path="/api/user/new",
    summary="Creation of new user",
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
    redis_user = await redis.hgetall(f"users:{user_in.login}")
    if redis_user:
        responce.status_code = status.HTTP_409_CONFLICT
        return {"message": "user with this login already exists"}

    user_out: UserOut = await UserIn.save(user_in)
    responce.status_code = status.HTTP_201_CREATED
    return user_out


@app.post(
    path="/api/user/login",
    summary="Login procedure",
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
async def login(user_in: UserIn, responce: Response):
    redis_user = await redis.hgetall(f"users:{user_in.login}")
    if not redis_user:
        responce.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "user not found"}
    m = hashlib.sha256()
    m.update(user_in.password.encode("utf-8"))
    if m.digest() == redis_user[b"hash"]:
        responce.status_code = status.HTTP_200_OK
        return {"token": random.randint(1000000000, 2000000000)}
    else:
        responce.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "invalid credentials"}
