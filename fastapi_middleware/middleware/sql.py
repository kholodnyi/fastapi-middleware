import logging
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
    def __init__(self, app, log_each_query: bool = False):
        super().__init__(app)

        self.log_each_query = log_each_query
        if log_each_query and not logger.isEnabledFor(logging.DEBUG):
            logger.warning(
                'SQLQueriesMiddleware is configured to log each query, '
                'but the logger is not configured to log DEBUG messages. '
                'Please set the fastapi-middleware logger level to DEBUG to see the queries.'
            )

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ):
        sql_queries_ctx.log_each_query = self.log_each_query

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

        # INFO summary log
        logger.info(
            f'[SQLQueriesMiddleware] Total Queries: {sql_queries_ctx.num_queries}, '
            f'Total Time: {self._pprint_time(total_time)}, '
            f'Avg Time: {self._pprint_time(avg_time)}, '
            f'Fastest: {self._pprint_time(sql_queries_ctx.fastest[0])}, '
            f'Slowest: {self._pprint_time(sql_queries_ctx.slowest[0])}'
        )

        # DEBUG detailed logs
        logger.debug(f'[SQLQueriesMiddleware] Fastest Query: {sql_queries_ctx.fastest[1]}')
        logger.debug(f'[SQLQueriesMiddleware] Slowest Query: {sql_queries_ctx.slowest[1]}')

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

    # remove newlines from the statement and make it a single line
    statement = ' '.join(statement.splitlines())

    try:
        sql_queries_ctx.query_times.append(total)

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

    if hasattr(sql_queries_ctx, 'log_each_query') and sql_queries_ctx.log_each_query:
        logger.debug(f'[SQLQueriesMiddleware] Query: {statement}, Time: {total:.2f}s')
