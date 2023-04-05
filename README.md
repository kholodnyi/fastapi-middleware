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

from fastapi_middleware import SQLQueriesMiddleware, RequestVarsMiddleware

...

app = FastAPI()

...

# set desired logging level
logging.getLogger("fastapi-middleware").setLevel(logging.DEBUG)

# add desired middleware
app.add_middleware(SQLQueriesMiddleware)
app.add_middleware(RequestVarsMiddleware)
```