from contextvars import ContextVar
import time

from sqlalchemy import event
from sqlalchemy.engine import Engine
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from fastapi_middleware.log import logger
from fastapi_middleware.utils import ContextObj, ContextVarProxy

sql_queries_ctx_var: ContextVar[ContextObj] = ContextVar('sql_queries_ctx', default=ContextObj())
sql_queries_ctx = ContextVarProxy(sql_queries_ctx_var)


class SQLQueriesMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ):
        sql_queries_ctx.num_queries = 0
        sql_queries_ctx.query_times = []
        sql_queries_ctx.fastest = (float('inf'), '')
        sql_queries_ctx.slowest = (float('-inf'), '')

        # perform the request
        response = await call_next(request)

        total_time = sum(sql_queries_ctx.query_times)
        try:
            avg_time = total_time / sql_queries_ctx.num_queries
        except ZeroDivisionError:
            avg_time = 0

        # INFO
        logger.info(f'[DB] Total number of SQL queries: {sql_queries_ctx.num_queries}')
        logger.info(f'[DB] Total time of SQL queries: {self._pprint_time(total_time)}')

        # DEBUG
        logger.debug(f'[DB] Average time of SQL query: {self._pprint_time(avg_time)}')
        logger.debug(f'[DB] Fastest query: {self._pprint_time(sql_queries_ctx.fastest[0])}')
        logger.debug(f'[DB] Fastest query statement: {sql_queries_ctx.fastest[1]}', )
        logger.debug(f'[DB] Slowest query: {self._pprint_time(sql_queries_ctx.slowest[0])}')
        logger.debug(f'[DB] Slowest query statement: {sql_queries_ctx.slowest[1]}', )
        return response

    @staticmethod
    def _pprint_time(total_time):
        if total_time > 1:
            return f'{total_time:.2f}s'
        else:
            return f'{total_time*1000:.2f}ms'


@event.listens_for(Engine, 'before_cursor_execute')
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    try:
        sql_queries_ctx.num_queries += 1
    except AttributeError:
        # handle initial DB queries on application startup or
        # when the middleware is not used
        sql_queries_ctx.num_queries = 1

    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, 'after_cursor_execute')
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)

    try:
        sql_queries_ctx.query_times.append(total)
        # compare total to fastest and slowest
        if total < sql_queries_ctx.fastest[0]:
            sql_queries_ctx.fastest = (total, statement)
        if total > sql_queries_ctx.slowest[0]:
            sql_queries_ctx.slowest = (total, statement)

    except AttributeError:
        # handle initial DB queries on application startup or
        # when the middleware is not used
        sql_queries_ctx.query_times = [total]
        sql_queries_ctx.fastest = (total, statement)
        sql_queries_ctx.slowest = (total, statement)
