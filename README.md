# OpenTelemetry Python Example

This is a simple example of using the OpenTelemetry Python SDK to create and export spans in OTLP JSON format to stdout.

This is useful as a shim for systems that don't support traces first class, but can consume OTLP JSON formatted spans in the form of logs.

## Installation

This is not published to PyPI, so you need to copy the `stdout_otlp_json_span_exporter.py` file into your project.

## Examples

See the `examples` directory for usage examples:

- `examples/run_stdout_otlp_json_span_exporter.py`: A simple script that creates a tracer provider, adds the `SimpleStdoutOtlpJsonSpanExporter`, creates a few spans, and then shuts down the provider to flush the spans.

After configuring the exporter, run the example script:

```bash
python examples/run_stdout_otlp_json_span_exporter.py
```

You should see OTLP JSON formatted spans printed to stdout.

```json
{"traceId":"0ac47f9c3bfb302b98500517c60d813c","spanId":"dcdceb7230fd5715","parentSpanId":"b4c1d0da99b6e49f","name":"child-0","startTimeUnixNano":"1756310754744863470","endTimeUnixNano":"1756310754795012149","attributes":{"index":0},"scope":{"name":"__main__"}}
{"traceId":"0ac47f9c3bfb302b98500517c60d813c","spanId":"edd2f29aa6ff43d6","parentSpanId":"b4c1d0da99b6e49f","name":"child-1","startTimeUnixNano":"1756310754795145418","endTimeUnixNano":"1756310754845248824","attributes":{"index":1},"scope":{"name":"__main__"}}
{"traceId":"0ac47f9c3bfb302b98500517c60d813c","spanId":"284d67d793dd4bce","parentSpanId":"b4c1d0da99b6e49f","name":"child-2","startTimeUnixNano":"1756310754845375782","endTimeUnixNano":"1756310754895513995","attributes":{"index":2},"scope":{"name":"__main__"}}
{"traceId":"0ac47f9c3bfb302b98500517c60d813c","spanId":"b4c1d0da99b6e49f","parentSpanId":"","name":"example-parent","startTimeUnixNano":"1756310754744791584","endTimeUnixNano":"1756310754895555012","attributes":{"example.attr":"parent"},"scope":{"name":"__main__"}}
```

The output can be configured to include / remove certain fields through the `omit_list` parameter of the `SimpleStdoutOtlpJsonSpanExporter`.

```python
    exporter = SimpleStdoutOtlpJsonSpanExporter(
        omit_list=[
            "spanId",
            "parentSpanId",
            "resource",
            "status",
            "kind",
            "scope",
        ]
    )
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    tracer = trace.get_tracer(__name__)
```

Then output will look as follows:

```json
{"traceId":"b809e4037204becb2e3b33756da94d74","name":"child-0","startTimeUnixNano":"1756310787766371890","endTimeUnixNano":"1756310787816517962","attributes":{"index":0}}
{"traceId":"b809e4037204becb2e3b33756da94d74","name":"child-1","startTimeUnixNano":"1756310787816641837","endTimeUnixNano":"1756310787866788836","attributes":{"index":1}}
{"traceId":"b809e4037204becb2e3b33756da94d74","name":"child-2","startTimeUnixNano":"1756310787866906342","endTimeUnixNano":"1756310787917046646","attributes":{"index":2}}
{"traceId":"b809e4037204becb2e3b33756da94d74","name":"example-parent","startTimeUnixNano":"1756310787766305824","endTimeUnixNano":"1756310787917085487","attributes":{"example.attr":"parent"}}
```

TraceId may be omitted as well if custom attributes are used to correlate spans.

## More Information

- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/instrumentation/python/)
- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/)
