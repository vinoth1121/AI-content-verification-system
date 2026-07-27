"""Prometheus metrics registry."""
from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

registry = CollectorRegistry()

http_requests_total = Counter(
    "acvs_http_requests_total",
    "Total HTTP requests by route/method/status",
    labelnames=("method", "route", "status"),
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "acvs_http_request_duration_seconds",
    "HTTP request latency in seconds",
    labelnames=("method", "route"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
    registry=registry,
)

scans_total = Counter(
    "acvs_scans_total",
    "Total scans initiated by modality",
    labelnames=("modality",),
    registry=registry,
)

scans_completed_total = Counter(
    "acvs_scans_completed_total",
    "Scans that finished successfully",
    labelnames=("modality", "label"),
    registry=registry,
)

scans_failed_total = Counter(
    "acvs_scans_failed_total",
    "Scans that raised an exception",
    labelnames=("modality",),
    registry=registry,
)

scan_duration_seconds = Histogram(
    "acvs_scan_duration_seconds",
    "AI engine inference latency in seconds",
    labelnames=("modality",),
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
    registry=registry,
)

auth_attempts_total = Counter(
    "acvs_auth_attempts_total",
    "Authentication attempts by outcome",
    labelnames=("outcome",),
    registry=registry,
)

active_users = Gauge(
    "acvs_active_users",
    "Total registered users (active + disabled)",
    registry=registry,
)


def metrics_response():
    from fastapi import Response
    return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
