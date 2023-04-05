import contextvars

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request


class RequestVars:
    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __delattr__(self, name):
        del self.__dict__[name]


request_vars = contextvars.ContextVar('request_vars', default=RequestVars())


class RequestVarsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ):
        request_vars.set(RequestVars())
        response = await call_next(request)
        return response
