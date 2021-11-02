Run locally

```
docker-compose up
```

Run the tests:

```
pytest
```

Run the application:

```
uvicorn app.main:app
```

Init db:

```
python -m app.init_db
```

Run redis in docker:

```
docker run -p 6379:6379 -d --name=redis redis:alpine
```

Build image:

```
docker build --tag=icecreamapi:0.0.4 .
```

Run container:

```
docker run --name=icecreamapi -d -p 8000:8000 icecreamapi:0.0.4
```

Run something inside container(e.g. python -m app.init_db)

```
docker exec -it <container_id> /bin/sh
```

TODO:

3. increase test coverage
4. ~~When add ice_cream load image and store it to static folder~~
4. Fix #1 (download files with no extension)
5. describe Caddy server on host
6. add project description
7. https://caddyserver.com/docs/caddyfile/directives/handle_errors -> oops, something goes wrong page
8. ~~split local packages like flake, isort, black from production~~


Был православный Caddyfile на проде:

```
:80

root * home/user/public

handle /static/* {
        uri strip_prefix /static
        file_server
}

```

Сдеал такой (полетит?)

```
:80

handle /static/* {
        root * /root/icecreamapi-app/icecreamapi/static
        uri strip_prefix /static
        file_server
}

reverse_proxy localhost:8000
```