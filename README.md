# Icecream API

This simple project provides REST API for mobile application. It uses Redis for store data. FastAPI as web-framework.

Redis isn't best solution for storing data, but i choose it for this project to get a little practice with it.

> Warning: carefully use redis as database in real production services. You may need look for other DBMS.

## Run locally with docker-compose

```
docker-compose up --build
```

## Run with uvicorn

```
uvicorn app.main:app
```

## You can run redis in docker

```
docker run -p 6379:6379 -d --name=redis redis:alpine
```

## Run tests:

```
pytest
```


## Init db:

```
python -m app.init_db
```


## Other docker utils

```
docker build --tag=icecreamapi:0.0.4 .  # Build image

docker run --name=icecreamapi -d -p 8000:8000 icecreamapi:0.0.4  # Run container with app

docker exec -it <container_id> /bin/sh  # Run something inside container(e.g. python -m app.init_db)
```

## Caddyfile in production:

```
:80


handle /static/* {
        root * /root/icecreamapi-app/icecreamapi/static
        uri strip_prefix /static
        file_server
}

reverse_proxy localhost:8000 {
    @error status 500 503
    handle_response @error {
        respond "{http.reverse_proxy.status_text}
                Ooops. Seems that you got error.
                Something goes wrong.
                If problem occur again, please contact me on Telegram @Medveddo."
    }
}
```

## Production server supplied with this software:

1. Caddy web server
2. Redis server
3. Python