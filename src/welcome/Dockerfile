FROM python:3-alpine
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8084
ENV OTEL_SERVICE_NAME=welcome
ENV OTEL_EXPORTER_OTLP_INSECURE=true
ENV OTEL_EXPORTER_OTLP_ENDPOINT=otel-collector.default:4317
ENV OTEL_TRACES_EXPORTER=otlp
#ENV OTEL_METRICS_EXPORTER=otlp,console1

COPY ./app .
RUN opentelemetry-bootstrap -a install
EXPOSE ${PORT}
CMD opentelemetry-instrument \
 waitress-serve --host 0.0.0.0 --port ${PORT} main:app