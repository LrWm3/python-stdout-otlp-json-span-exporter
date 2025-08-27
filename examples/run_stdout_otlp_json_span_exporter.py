# examples/run_stdout_otlp_json_span_exporter.py
"""
Minimal example that demonstrates using the stdout OTLP JSON span exporter
from this project.

Run with:
  uv run examples/run_stdout_otlp_json_span_exporter.py

This example:
- Creates a tracer provider
- Adds the project's StdoutOtlpJsonSpanExporter via a BatchSpanProcessor
- Emits a few spans
- Shuts down the provider so spans are flushed
"""

import time
import sys

# Ensure src is on path when running from project root
if "src" not in sys.path:
    sys.path.insert(0, "src")

from stdout_otlp_json_span_exporter import SimpleStdoutOtlpJsonSpanExporter
from opentelemetry.trace import get_tracer_provider, set_tracer_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace


def main():
    # Create SDK tracer provider and set globally
    provider = TracerProvider()
    set_tracer_provider(provider)

    # Create exporter from this repo and add to provider via BatchSpanProcessor
    exporter = SimpleStdoutOtlpJsonSpanExporter()
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    tracer = trace.get_tracer(__name__)

    # Create a few example spans
    with tracer.start_as_current_span("example-parent") as parent:
        parent.set_attribute("example.attr", "parent")
        for i in range(3):
            with tracer.start_as_current_span(f"child-{i}") as child:
                child.set_attribute("index", i)
                time.sleep(0.05)

    # Ensure processor/exporter flush on shutdown
    provider.shutdown()
    print("Finished exporting spans to stdout (OTLP JSON format).")


if __name__ == "__main__":
    main()
