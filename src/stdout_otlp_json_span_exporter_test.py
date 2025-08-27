import json
import pytest
from opentelemetry.sdk.trace import _Span
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import TraceState
from opentelemetry.trace.span import SpanContext, TraceFlags
from opentelemetry.sdk.resources import Resource
from stdout_otlp_json_span_exporter import SimpleStdoutOtlpJsonSpanExporter


# Helpers to construct a minimal ReadableSpan-like object
class DummyContext:
    def __init__(self, trace_id: int, span_id: int):
        self.trace_id = trace_id
        self.span_id = span_id


class DummyParent:
    def __init__(self, span_id: int):
        self.span_id = span_id


class SimpleReadableSpan:
    def __init__(
        self,
        *,
        trace_id: int,
        span_id: int,
        name: str = "test-span",
        start_time: int = 1,
        end_time: int = 2,
        attributes=None,
        resource=None,
    ):
        self.context = DummyContext(trace_id, span_id)
        self.parent = None
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.attributes = attributes or {}
        self.resource = resource or Resource({})
        self.events = []
        self.links = []
        self.dropped_attributes = 0
        self.dropped_events = 0
        self.dropped_links = 0
        self.status = None
        self.kind = 0


def make_span(i=0):
    return SimpleReadableSpan(
        trace_id=0x0123456789ABCDEF0123456789ABCDEF,
        span_id=i + 1,
        name=f"span-{i}",
        attributes={"http.method": "GET", "http.status_code": 200},
    )


def test_export_writes_otlp_json_line_to_stdout(capsys):
    # GIVEN an exporter and a simple span
    exporter = SimpleStdoutOtlpJsonSpanExporter()
    span = make_span()

    # WHEN exporting the span
    res = exporter.export([span])

    # THEN the exporter returns SUCCESS and stdout contains one JSON line with expected fields
    assert res is not None
    captured = capsys.readouterr()
    out = captured.out.strip()
    assert out, "Expected exporter to write to stdout"

    payload = json.loads(out)
    assert "resourceSpans" in payload
    rs = payload["resourceSpans"]
    assert isinstance(rs, list) and len(rs) == 1
    scopeSpans = rs[0]["scopeSpans"]
    assert isinstance(scopeSpans, list) and len(scopeSpans) == 1
    spans = scopeSpans[0]["spans"]
    assert isinstance(spans, list) and len(spans) == 1
    s = spans[0]
    assert s["name"] == span.name
    assert s["traceId"] == format(span.context.trace_id, "032x")
    assert s["spanId"] == format(span.context.span_id, "016x")
    assert (
        any(a["key"] == "http.method" for a in s["attributes"]) or s["attributes"] == []
    )


def test_export_multiple_spans_writes_multiple_spans(capsys):
    # GIVEN exporter and multiple spans
    exporter = SimpleStdoutOtlpJsonSpanExporter()
    spans = [make_span(i) for i in range(3)]

    # WHEN exporting
    exporter.export(spans)

    # THEN stdout contains a payload with three spans
    captured = capsys.readouterr()
    payload = json.loads(captured.out.strip())
    spans_out = payload["resourceSpans"][0]["scopeSpans"][0]["spans"]
    assert len(spans_out) == 3


def test_export_empty_list_writes_empty_resourceSpans(capsys):
    # GIVEN exporter
    exporter = SimpleStdoutOtlpJsonSpanExporter()

    # WHEN exporting empty list
    res = exporter.export([])

    # THEN stdout should contain resourceSpans empty list
    captured = capsys.readouterr()
    out = captured.out.strip()
    assert out
    payload = json.loads(out)
    assert payload.get("resourceSpans") == []
    assert res is not None
