"""OpenTelemetry: traces + metrics + logs -> OTLP collector -> Jaeger / Prometheus."""
import logging

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings
from app.core.database import engine

tracer = trace.get_tracer("sql-lab")
_meter = metrics.get_meter("sql-lab")
scenario_counter = _meter.create_counter("sql_scenarios_total", description="SQL scenarios executed")
scenario_duration = _meter.create_histogram("sql_scenario_duration_ms", unit="ms")


def setup_telemetry(service_name: str, app=None) -> None:
    ep = settings.otlp_endpoint
    resource = Resource.create({"service.name": service_name})

    tp = TracerProvider(resource=resource)
    tp.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=ep, insecure=True)))
    trace.set_tracer_provider(tp)

    reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=ep, insecure=True), export_interval_millis=10_000)
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))

    lp = LoggerProvider(resource=resource)
    lp.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=ep, insecure=True)))
    set_logger_provider(lp)
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(LoggingHandler(level=logging.INFO, logger_provider=lp))

    SQLAlchemyInstrumentor().instrument(engine=engine)
    if app is not None:
        FastAPIInstrumentor.instrument_app(app)
