import time

from sqlalchemy import event
from sqlalchemy.engine import Engine
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from fastapi_middleware.log import logger
from fastapi_middleware.requestvars import request_vars


class SQLQueriesMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ):
        request_vars.get().num_queries = 0
        request_vars.get().query_times = []
        request_vars.get().fastest = (float('inf'), '')
        request_vars.get().slowest = (float('-inf'), '')

        # perform the request
        response = await call_next(request)

        total_time = sum(request_vars.get().query_times)
        try:
            avg_time = total_time / request_vars.get().num_queries
        except ZeroDivisionError:
            avg_time = 0

        # INFO
        logger.info(f'[DB] Total number of SQL queries: {request_vars.get().num_queries}')
        logger.info(f'[DB] Total time of SQL queries: {self._pprint_time(total_time)}')

        # DEBUG
        logger.debug(f'[DB] Average time of SQL query: {self._pprint_time(avg_time)}')
        logger.debug(f'[DB] Fastest query: {self._pprint_time(request_vars.get().fastest[0])}')
        logger.debug(f'[DB] Fastest query statement: {request_vars.get().fastest[1]}', )
        logger.debug(f'[DB] Slowest query: {self._pprint_time(request_vars.get().slowest[0])}')
        logger.debug(f'[DB] Slowest query statement: {request_vars.get().slowest[1]}', )
        return response

    @staticmethod
    def _pprint_time(total_time):
        if total_time > 1:
            return f'{total_time:.2f}s'
        else:
            return f'{total_time*1000:.2f}ms'


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    try:
        request_vars.get().num_queries += 1
    except AttributeError:
        # handle initial DB queries on application startup or
        # when the middleware is not used
        request_vars.get().num_queries = 1

    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)

    try:
        request_vars.get().query_times.append(total)
        # compare total to fastest and slowest
        if total < request_vars.get().fastest[0]:
            request_vars.get().fastest = (total, statement)
        if total > request_vars.get().slowest[0]:
            request_vars.get().slowest = (total, statement)

    except AttributeError:
        # handle initial DB queries on application startup or
        # when the middleware is not used
        request_vars.get().query_times = [total]
        request_vars.get().fastest = (total, statement)
        request_vars.get().slowest = (total, statement)
