import logging
import time

from django.db import connection


logger = logging.getLogger("philonet")


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in {'/accounts/login/', '/signup/'}:
            return self.get_response(request)
        start = time.monotonic()
        query_count = 0
        query_ms = 0.0

        def _wrapper(execute, sql, params, many, context):
            nonlocal query_count, query_ms
            q_start = time.monotonic()
            try:
                return execute(sql, params, many, context)
            finally:
                query_count += 1
                query_ms += (time.monotonic() - q_start) * 1000

        with connection.execute_wrapper(_wrapper):
            response = self.get_response(request)
        duration_ms = (time.monotonic() - start) * 1000
        logger.info(
            "Timing %s %s %.1fms db=%.1fms queries=%d",
            request.method,
            request.path,
            duration_ms,
            query_ms,
            query_count,
        )
        return response
