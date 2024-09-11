# [FastAPI](https://fastapi.tiangolo.com/) middleware

## Introduction

`fastapi-middleware` is a set of middlewares for [FastAPI](https://fastapi.tiangolo.com/) framework.
## Installation

```shell
pip install fastapi-middleware
```

## Usage

To use middleware, you need to import it and add to your FastAPI app:

```python
from fastapi import FastAPI

...

from fastapi_middleware import (
    GlobalContextMiddleware,
    global_ctx,
    SQLQueriesMiddleware,
)

...

app = FastAPI()

...

# set desired logging level
logging.getLogger("fastapi-middleware").setLevel(logging.DEBUG)

# add desired middleware
app.add_middleware(SQLQueriesMiddleware)
app.add_middleware(GlobalContextMiddleware)


@app.get("/test")
def get_test():
    global_ctx.foo = 'bar'
    return {'ok': True}
```

`GlobalContextMiddleware` gives you a global context object (`global_ctx`) to store data during the lifetime of the request. You can add request-specific data, for example, in other middleware and use it across application.

`SQLQueriesMiddleware` would log insights about SQL queries made with SQLAlchemy like total number of queries, total duration, slowest/fastest queries, etc.