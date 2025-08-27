# OpenTelemetry Python Example

This is a simple example of using the OpenTelemetry Python SDK to create and export spans in OTLP JSON format to stdout.

This is useful as a shim for systems that don't support traces first class, but can consume OTLP JSON formatted spans in the form of logs.

## Installation

This is not published to PyPI, so you need to copy the `stdout_otlp_json_span_exporter.py` file into your project.

## Examples

See the `examples` directory for usage examples:

- `examples/run_stdout_otlp_json_span_exporter.py`: A simple script that creates a tracer provider, adds the `SimpleStdoutOtlpJsonSpanExporter`, creates a few spans, and then shuts down the provider to flush the spans.

## More Information

- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/instrumentation/python/)
- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/)
