import time
import uuid
import logging
from functools import wraps

from flask import request, g, has_request_context

logger = logging.getLogger("request_trace")


class RequestTracingMiddleware:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_request(self._teardown_request)

        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s [%(trace_id)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    @staticmethod
    def _before_request():
        g.trace_id = request.headers.get("X-Trace-ID", uuid.uuid4().hex[:16])
        g.request_start = time.time()
        logger.info(
            "%s %s started (client: %s, ua: %s)",
            request.method,
            request.path,
            request.remote_addr,
            request.user_agent.string[:100],
            extra={"trace_id": g.trace_id},
        )

    @staticmethod
    def _after_request(response):
        duration_ms = (time.time() - g.get("request_start", time.time())) * 1000
        response.headers["X-Trace-ID"] = g.get("trace_id", "unknown")
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

        log_method = logger.info if response.status_code < 400 else logger.warning
        log_method(
            "%s %s → %d (%.2fms, %s bytes)",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            response.content_length or 0,
            extra={"trace_id": g.get("trace_id", "unknown")},
        )
        return response

    @staticmethod
    def _teardown_request(exception):
        if exception:
            logger.error(
                "Request failed with exception: %s",
                str(exception),
                extra={"trace_id": g.get("trace_id", "unknown")},
                exc_info=True,
            )


def log_slow_requests(threshold_ms=1000):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            elapsed_ms = (time.time() - start) * 1000
            if elapsed_ms > threshold_ms:
                logger.warning(
                    "SLOW REQUEST: %s took %.2fms (threshold: %dms)",
                    f.__name__,
                    elapsed_ms,
                    threshold_ms,
                    extra={"trace_id": g.get("trace_id", "n/a")},
                )
            return result

        return wrapper

    return decorator
