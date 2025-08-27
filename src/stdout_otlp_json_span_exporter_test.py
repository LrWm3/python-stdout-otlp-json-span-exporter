import json
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
        self.status = type(
            "Status",
            (),
            {"status_code": type("StatusCode", (), {"value": 0}), "description": ""},
        )()


def make_span(i=0):
    return SimpleReadableSpan(
        trace_id=0x0123456789ABCDEF0123456789ABCDEF,
        span_id=i + 1,
        name=f"span-{i}",
        attributes={"http.method": "GET", "http.status_code": 200},
    )


def test_export_writes_otlp_json_line_to_stdout(capsys):
    # GIVEN an exporter and a simple span
    exporter = SimpleStdoutOtlpJsonSpanExporter(omit_list=[])
    span = make_span()

    # WHEN exporting the span
    res = exporter.export([span])  # pyright: ignore[reportArgumentType]

    # THEN the exporter returns SUCCESS and stdout contains one JSON line with expected fields
    assert res is not None
    captured = capsys.readouterr()
    out = captured.out.strip()
    assert out, "Expected exporter to write to stdout"


def test_export_multiple_spans_writes_multiple_spans(capsys):
    # GIVEN exporter and multiple spans
    exporter = SimpleStdoutOtlpJsonSpanExporter(omit_list=[])
    spans = [make_span(i) for i in range(3)]

    # WHEN exporting
    exporter.export(spans)  # pyright: ignore[reportArgumentType]

    # THEN stdout contains a payload with three spans
    captured = capsys.readouterr()
    assert captured.out, "Expected exporter to write to stdout"

    lines = captured.out.strip().split("\n")
    assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
    for i, line in enumerate(lines):
        obj = json.loads(line)
        assert obj["name"] == f"span-{i}"
        assert obj["spanId"] == f"{i + 1:016x}"
        assert obj["traceId"] == "0123456789abcdef0123456789abcdef"
        assert obj["attributes"]["http.method"] == "GET"
        assert obj["attributes"]["http.status_code"] == 200
        assert "resource" in obj
        assert "status" in obj
        assert "kind" in obj
        assert "scope" in obj
        assert "events" not in obj
        assert "links" not in obj
