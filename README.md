# [FastAPI](https://fastapi.tiangolo.com/) middleware

## Overview

`fastapi-middleware` provides a collection of middleware for enhancing [FastAPI](https://fastapi.tiangolo.com/) applications.

## Installation

Install `fastapi-middleware` directly from PyPI:

```shell
pip install fastapi-middleware
```

## Getting Started

To start using the middleware, import the components you need and add them to your FastAPI app.

### Example usage
```python
import logging

from fastapi import FastAPI
from fastapi_middleware import SQLQueriesMiddleware

app = FastAPI()

# Set logging level for middleware
logging.getLogger('fastapi-middleware').setLevel(logging.DEBUG)

# Add the middleware components
app.add_middleware(SQLQueriesMiddleware)
```

## Middleware Components

### `GlobalContextMiddleware`

The GlobalContextMiddleware provides a global context object (`global_ctx`) that allows you to store data throughout the lifetime of a request. This can be useful for sharing request-specific information across different parts of your application without needing to pass it explicitly.

#### Example Use Case
Add data to the global_ctx in one part of your application, and access it in other middleware or endpoint functions:

```python
from fastapi import FastAPI
from fastapi_middleware import GlobalContextMiddleware, global_ctx

app = FastAPI()

# Add the middleware components
app.add_middleware(GlobalContextMiddleware)

...

global_ctx.user_id = 12345  # Set user-specific data
global_ctx.foo = 'bar'      # Or set request-specific data
# Retrieve in other parts of the app: global_ctx.user_id, global_ctx.foo
```

### `SQLQueriesMiddleware`
The `SQLQueriesMiddleware` logs a concise summary of SQL query performance in a single `INFO` message for each request, making it easy to monitor query performance. Additionally, detailed query insights, such as the actual SQL statements of the fastest and slowest queries, as well as individual query statements, are available at the `DEBUG` level if configured. 

Key metrics include:

- Total SQL Queries: Number of SQL queries executed.
- Total Query Time: Combined execution time for all queries.
- Average Query Time: Average time taken per query.
- Fastest and Slowest Query Times: Execution times of the fastest and slowest queries, along with statements at DEBUG level.

#### Configuration
You can customize `SQLQueriesMiddleware` with the following option:

- `print_each_query` (bool): If `True`, logs each individual SQL query's time and statement at the `DEBUG` level. This setting is useful for in-depth debugging. Default is `False`.

#### Example Usage
```python
# Add SQLQueriesMiddleware with configuration
app.add_middleware(SQLQueriesMiddleware, print_each_query=True)
```

#### Example Log Output
```text
INFO:     [SQLQueriesMiddleware] Total Queries: 4, Total Time: 24.04ms, Avg Time: 6.01ms, Fastest: 0.46ms, Slowest: 13.30ms
DEBUG:    [SQLQueriesMiddleware] Fastest Query: Fastest Query: SELECT * FROM users WHERE id = 1;
DEBUG:    [SQLQueriesMiddleware] Slowest Query: SELECT * FROM orders WHERE status = 'pending';
```