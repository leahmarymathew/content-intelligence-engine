from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generator, TypeVar

from fastapi import Request

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(slots=True)
class StageTrace:
    """Captures latency and error details for one pipeline stage."""

    stage: str
    latency_ms: float
    ok: bool
    error: str | None = None


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured JSON logging once at process startup."""

    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(message)s")


def get_logger(name: str) -> logging.Logger:
    """Return a module logger."""

    return logging.getLogger(name)


def log_event(logger: logging.Logger, event: str, **kwargs: Any) -> None:
    """Emit a structured JSON log event."""

    payload = {"event": event, **kwargs}
    logger.info(json.dumps(payload, default=str))


@contextmanager
def stage_timer(stage: str, traces: list[StageTrace]) -> Generator[None, None, None]:
    """Context manager for measuring stage latency and capturing exceptions."""

    start = time.perf_counter()
    try:
        yield
        traces.append(StageTrace(stage=stage, latency_ms=(time.perf_counter() - start) * 1000, ok=True))
    except Exception as exc:  # noqa: BLE001
        traces.append(
            StageTrace(stage=stage, latency_ms=(time.perf_counter() - start) * 1000, ok=False, error=str(exc))
        )
        raise


def traced(stage: str) -> Callable[[F], F]:
    """Decorator to add coarse-grained tracing for service methods."""

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger(func.__module__)
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                log_event(logger, "stage_completed", stage=stage, latency_ms=(time.perf_counter() - start) * 1000)
                return result
            except Exception as exc:  # noqa: BLE001
                log_event(
                    logger,
                    "stage_failed",
                    stage=stage,
                    latency_ms=(time.perf_counter() - start) * 1000,
                    error=str(exc),
                )
                raise

        return async_wrapper  # type: ignore[return-value]

    return decorator


async def add_request_context(request: Request, call_next: Callable[..., Any]) -> Any:
    """FastAPI middleware helper for request-level latency and route tracing."""

    logger = logging.getLogger("api")
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    log_event(
        logger,
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        latency_ms=elapsed_ms,
    )
    response.headers["X-Request-Latency-Ms"] = f"{elapsed_ms:.2f}"
    return response
