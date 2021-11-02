from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware

from .endpoints import router
from .settings import REDIS_CLIENT

app = FastAPI(
    title="IceCreamAPI",
    description="This service is MVP (ultra-minimal 😊) of API for mobile app",
    version="0.0.5",
    contact={
        "name": "Sizikov Vitaly",
        "url": "https://vk.com/vitaliksiz",
        "email": "sizikov.vitaly@gmail.com",
    },
)
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    await REDIS_CLIENT.incr("health")
    print("SUCCESS:\tRedis initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    await REDIS_CLIENT.close()
    print("SUCCESS:\tRedis connection was closed")
