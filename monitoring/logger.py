"""
monitoring/logger.py
────────────────────────────────────────────
AOIP Observability Layer

Features:
    • Prometheus metrics
    • optional Langfuse tracing
    • latency + success/error tracking
"""

import os
import time
from functools import wraps

from prometheus_client import Counter, Histogram, start_http_server

try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None


# ───────── PROMETHEUS METRICS ─────────
REQUEST_COUNT = Counter(
    "aoip_requests_total",
    "Total number of AOIP requests processed",
    ["component", "status"]
)

REQUEST_LATENCY = Histogram(
    "aoip_request_latency_seconds",
    "Latency per AOIP component",
    ["component"]
)


# ───────── LANGFUSE CONFIG ─────────
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

lf = None
if Langfuse and LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    try:
        lf = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY
        )
        print("🧠 Langfuse tracing enabled")
    except Exception as e:
        print(f"⚠️ Langfuse init failed: {e}")


# ───────── DECORATOR ─────────
def monitor(component: str):
    """
    Decorator for latency + request count + optional Langfuse tracing.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                status = "error"
                raise
            finally:
                latency = time.time() - start_time

                REQUEST_COUNT.labels(
                    component=component,
                    status=status
                ).inc()

                REQUEST_LATENCY.labels(
                    component=component
                ).observe(latency)

                if lf:
                    try:
                        lf.trace(
                            name=component,
                            metadata={
                                "status": status,
                                "latency_s": round(latency, 3)
                            }
                        )
                    except Exception:
                        pass

        return wrapper

    return decorator


# ───────── METRICS SERVER ─────────
_metrics_started = False


def start_metrics_server(port: int = 9100):
    """
    Starts Prometheus metrics endpoint once.
    Safe for Streamlit reruns.
    """
    global _metrics_started

    if _metrics_started:
        return

    start_http_server(port)
    _metrics_started = True

    print(f"📡 Prometheus metrics → http://localhost:{port}/metrics")