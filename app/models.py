from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class OrderPosition(BaseModel):
    icecream_id: int
    quantity: int

    class Config:
        schema_extra = {
            "example": {
                "icecream_id": 1,
                "quantity": 2,
            }
        }


class Order(BaseModel):
    id: int
    user_login: str
    created_at: datetime
    positions: List[OrderPosition]


class User(BaseModel):
    login: str
    hash_: bytes


class UserOut(BaseModel):
    login: str
    created_at: datetime = datetime.now()

    class Config:
        schema_extra = {
            "example": {
                "login": "bestboss",
                "created_at": datetime(2021, 10, 23, 12, 56),
            }
        }


class UserIn(BaseModel):
    login: str
    password: str

    class Config:
        schema_extra = {"example": {"login": "bestboss", "password": "Pa$$w0rd!"}}


class IceCream(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    price: Optional[float] = 0
    weight: Optional[float] = 0
    img_url: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Hot Summer",
                "img_url": "https://media-cdn.tripadvisor.com/media/photo-s/18/7c/da/68/bonmot-ice-cream.jpg",
                "price": 35.4,
                "weight": 50.0,
            }
        }


class ResponceDetail(BaseModel):
    detail: str


class SuccessToken(BaseModel):
    token: int
