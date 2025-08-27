import sys, json, threading, typing
from typing import Sequence, Dict, Any, List

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.resources import Resource


def _any_value(v: Any) -> Dict[str, Any]:
    if isinstance(v, bool):
        return {"boolValue": v}
    if isinstance(v, int):
        return {"intValue": v}
    if isinstance(v, float):
        return {"doubleValue": v}
    if isinstance(v, str):
        return {"stringValue": v}
    if isinstance(v, (list, tuple)):
        return {"arrayValue": {"values": [_any_value(x) for x in v]}}
    if isinstance(v, dict):
        return {
            "kvlistValue": {
                "values": [{"key": k, "value": _any_value(val)} for k, val in v.items()]
            }
        }
    return {"stringValue": str(v)}


def _attrs(attributes: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"key": k, "value": _any_value(v)} for k, v in (attributes or {}).items()]


def _hex_trace_id(tid: int) -> str:
    return format(tid, "032x")


def _hex_span_id(sid: int) -> str:
    return format(sid, "016x")


DEFAULT_OMIT_LIST = ["resource", "status", "kind"]


class SimpleStdoutOtlpJsonSpanExporter(SpanExporter):
    """
    Export each span as a single JSON line to stdout.

    Includes resource attributes and scope info inline for correlation.

    Parameters
    ----------

    resource: The resource associated with the spans being exported. (default: new resource)
    omit_list: A list of fields to exclude from the exported spans. (default: resource, status, kind)
    """

    def __init__(
        self, resource: Resource | None = None, omit_list: list[str] | None = None
    ) -> None:
        self._stopped = False
        self._lock = threading.Lock()
        self._resource = resource or Resource.create({})
        self._omit_list = omit_list or DEFAULT_OMIT_LIST

    def shutdown(self) -> None:
        self._stopped = True

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        if self._stopped:
            return SpanExportResult.FAILURE

        with self._lock:
            for s in spans:
                ctx = s.context
                parent = s.parent

                scope = getattr(s, "instrumentation_scope", None) or getattr(
                    s, "instrumentation_info", None
                )
                scope_dict = {}
                if scope:
                    if getattr(scope, "name", None):
                        scope_dict["name"] = scope.name
                    if getattr(scope, "version", None):
                        scope_dict["version"] = scope.version

                obj = {
                    "traceId": _hex_trace_id(ctx.trace_id),
                    "spanId": _hex_span_id(ctx.span_id),
                    "parentSpanId": (
                        "" if parent is None else _hex_span_id(parent.span_id)
                    ),
                    "name": s.name,
                    # omit kind
                    # "kind": str(s.kind),
                    "startTimeUnixNano": str(s.start_time),
                    "endTimeUnixNano": str(s.end_time),
                    "attributes": _attrs(s.attributes or {}),
                    "status": {
                        "code": getattr(s.status.status_code, "value", 0),
                        "message": getattr(s.status, "description", None),
                    },
                    "resource": {"attributes": _attrs(self._resource.attributes)},
                    "scope": scope_dict,
                    "events": [
                        {
                            "timeUnixNano": str(ev.timestamp),
                            "name": ev.name,
                            "attributes": _attrs(ev.attributes or {}),
                        }
                        for ev in (s.events or [])
                    ],
                    "links": [
                        {
                            "traceId": _hex_trace_id(l.context.trace_id),
                            "spanId": _hex_span_id(l.context.span_id),
                            "attributes": _attrs(l.attributes or {}),
                        }
                        for l in (s.links or [])
                    ],
                }

                if not obj["events"]:
                    obj.pop("events")
                if not obj["links"]:
                    obj.pop("links")
                if not obj["scope"]:
                    obj.pop("scope")

                for omit in self._omit_list:
                    obj.pop(omit, None)

                sys.stdout.write(json.dumps(obj, separators=(",", ":")) + "\n")
            sys.stdout.flush()

        return SpanExportResult.SUCCESS
