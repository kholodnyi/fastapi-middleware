from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from fastapi_middleware.utils import ContextObj, ContextVarProxy

global_ctx_var: ContextVar[ContextObj] = ContextVar('global_ctx', default=ContextObj())
global_ctx = ContextVarProxy(global_ctx_var)


class GlobalContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ):
        global_ctx_var.set(ContextObj())

        response = await call_next(request)

        global_ctx_var.set(ContextObj())
        return response
