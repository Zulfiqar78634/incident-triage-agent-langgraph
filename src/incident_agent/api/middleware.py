"""HTTP middleware guardrails for the agent API."""

from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

RequestHandler = Callable[[Request], Awaitable[Response]]


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assigns a request ID for tracing and returns it to the caller."""

    async def dispatch(self, request: Request, call_next: RequestHandler) -> Response:
        request_id = request.headers.get("x-request-id") or f"req_{uuid.uuid4().hex[:16]}"
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds baseline HTTP security headers."""

    async def dispatch(self, request: Request, call_next: RequestHandler) -> Response:
        response = await call_next(request)
        response.headers.setdefault("x-content-type-options", "nosniff")
        response.headers.setdefault("x-frame-options", "DENY")
        response.headers.setdefault("referrer-policy", "no-referrer")
        response.headers.setdefault(
            "content-security-policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
        )
        return response


class PayloadSizeLimitMiddleware(BaseHTTPMiddleware):
    """Rejects oversized request bodies before they reach application handlers."""

    def __init__(self, app: FastAPI, max_bytes: int = 100_000) -> None:
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next: RequestHandler) -> Response:
        content_length = request.headers.get("content-length")

        if content_length and content_length.isdigit() and int(content_length) > self.max_bytes:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request payload exceeds the allowed size."},
            )

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory per-client rate limiter for local API protection."""

    def __init__(self, app: FastAPI, max_requests: int = 30, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: RequestHandler) -> Response:
        client_id = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = self._requests[client_id]

        while window and now - window[0] > self.window_seconds:
            window.popleft()

        if len(window) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please retry later."},
            )

        window.append(now)
        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Converts unexpected exceptions into a structured API error response."""

    async def dispatch(self, request: Request, call_next: RequestHandler) -> Response:
        try:
            return await call_next(request)
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"detail": "An unexpected error occurred."},
            )


def add_guardrails(app: FastAPI, *, max_payload_bytes: int = 100_000) -> None:
    """Register the API guardrail middleware stack."""

    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(PayloadSizeLimitMiddleware, max_bytes=max_payload_bytes)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)
