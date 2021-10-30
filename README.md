Run the application:

```
uvicorn app.main:app
```

Run the tests:

```
python -m unittest app/tests.py
```

TODO: 

2. create init script to load ice.json to redis
3. increase test coverage
4. docker-compose
5. When add ice_cream load image and store it to static folder
6. describe Caddy server on host