"""HTTP middleware that records Prometheus metrics for every request."""
from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import http_requests_total, http_request_duration_seconds


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in ("/metrics", "/health", "/"):
            return await call_next(request)

        start = time.perf_counter()
        try:
            response = await call_next(request)
            duration = time.perf_counter() - start
            route = request.scope.get("route")
            route_path = getattr(route, "path", None) or request.url.path
            http_requests_total.labels(
                method=request.method, route=route_path, status=str(response.status_code),
            ).inc()
            http_request_duration_seconds.labels(
                method=request.method, route=route_path,
            ).observe(duration)
            return response
        except Exception:
            duration = time.perf_counter() - start
            route = request.scope.get("route")
            route_path = getattr(route, "path", None) or request.url.path
            http_requests_total.labels(
                method=request.method, route=route_path, status="500",
            ).inc()
            http_request_duration_seconds.labels(
                method=request.method, route=route_path,
            ).observe(duration)
            raise
