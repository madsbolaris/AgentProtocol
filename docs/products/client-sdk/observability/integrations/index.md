# Observability Integrations

Connect Client SDK with popular observability platforms and tools.

## Overview

Integrate your Agent Protocol application with industry-standard observability platforms for comprehensive monitoring, logging, tracing, and alerting.

---

## Supported Integrations

### Application Performance Monitoring (APM)

- **Datadog** - Full-stack observability platform
- **New Relic** - Application performance monitoring
- **Dynatrace** - AI-powered full-stack monitoring
- **AppDynamics** - Business performance monitoring

### Logging Platforms

- **Splunk** - Log management and analysis
- **Elasticsearch (ELK Stack)** - Search and analytics
- **Sumo Logic** - Cloud-native logging
- **Loggly** - Cloud-based log management

### Distributed Tracing

- **Jaeger** - Open-source distributed tracing
- **Zipkin** - Distributed tracing system
- **AWS X-Ray** - Distributed tracing for AWS
- **OpenTelemetry** - Vendor-neutral observability framework

### Metrics and Alerting

- **Prometheus** - Metrics collection and alerting
- **Grafana** - Metrics visualization and dashboards
- **CloudWatch** - AWS monitoring and observability
- **Azure Monitor** - Azure-native monitoring

---

## OpenTelemetry Integration

OpenTelemetry provides a vendor-neutral standard for observability.

=== "Python"

    ```python
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from microsoft.agents import AgentProtocolClient

    # Configure OpenTelemetry
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    span_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(span_exporter)
    )

    # Configure metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint="http://localhost:4317")
    )
    metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
    meter = metrics.get_meter(__name__)

    # Create custom metrics
    message_counter = meter.create_counter(
        "agent.messages.sent",
        description="Number of messages sent"
    )
    latency_histogram = meter.create_histogram(
        "agent.message.latency",
        description="Message processing latency"
    )

    # Instrument your code
    async def send_message_traced(message: str):
        with tracer.start_as_current_span("send_message") as span:
            span.set_attribute("message.length", len(message))

            start_time = time.time()
            try:
                response = await client.send_one_off(message)
                message_counter.add(1, {"status": "success"})
                return response
            except Exception as e:
                span.set_attribute("error", True)
                span.record_exception(e)
                message_counter.add(1, {"status": "error"})
                raise
            finally:
                latency = time.time() - start_time
                latency_histogram.record(latency * 1000)  # Convert to ms
    ```

=== "TypeScript"

    ```typescript
    import { NodeSDK } from '@opentelemetry/sdk-node';
    import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
    import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-grpc';
    import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-grpc';
    import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
    import { AgentProtocolClient } from '@microsoft/agents-client';

    // Initialize OpenTelemetry SDK
    const sdk = new NodeSDK({
      traceExporter: new OTLPTraceExporter({
        url: 'http://localhost:4317'
      }),
      metricReader: new PeriodicExportingMetricReader({
        exporter: new OTLPMetricExporter({
          url: 'http://localhost:4317'
        })
      }),
      instrumentations: [getNodeAutoInstrumentations()]
    });

    sdk.start();

    // Create custom metrics
    const { metrics } = require('@opentelemetry/api');
    const meter = metrics.getMeter('agent-protocol-client');

    const messageCounter = meter.createCounter('agent.messages.sent', {
      description: 'Number of messages sent'
    });

    const latencyHistogram = meter.createHistogram('agent.message.latency', {
      description: 'Message processing latency'
    });

    // Instrument your code
    import { trace, context, SpanStatusCode } from '@opentelemetry/api';

    async function sendMessageTraced(message: string) {
      const tracer = trace.getTracer('agent-client');
      const span = tracer.startSpan('send_message');

      span.setAttribute('message.length', message.length);

      const startTime = Date.now();
      try {
        const response = await client.sendOneOff(message);
        messageCounter.add(1, { status: 'success' });
        span.setStatus({ code: SpanStatusCode.OK });
        return response;
      } catch (error) {
        span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
        span.recordException(error);
        messageCounter.add(1, { status: 'error' });
        throw error;
      } finally {
        const latency = Date.now() - startTime;
        latencyHistogram.record(latency, { operation: 'send_message' });
        span.end();
      }
    }

    // Graceful shutdown
    process.on('SIGTERM', () => {
      sdk.shutdown().then(() => process.exit(0));
    });
    ```

=== "C#"

    ```csharp
    using OpenTelemetry;
    using OpenTelemetry.Resources;
    using OpenTelemetry.Trace;
    using OpenTelemetry.Metrics;
    using Microsoft.Agents.Client;
    using System.Diagnostics;

    // Configure OpenTelemetry
    var resourceBuilder = ResourceBuilder
        .CreateDefault()
        .AddService("agent-protocol-client");

    // Configure tracing
    using var tracerProvider = Sdk.CreateTracerProviderBuilder()
        .SetResourceBuilder(resourceBuilder)
        .AddSource("AgentProtocol")
        .AddOtlpExporter(options =>
        {
            options.Endpoint = new Uri("http://localhost:4317");
        })
        .Build();

    // Configure metrics
    using var meterProvider = Sdk.CreateMeterProviderBuilder()
        .SetResourceBuilder(resourceBuilder)
        .AddMeter("AgentProtocol")
        .AddOtlpExporter(options =>
        {
            options.Endpoint = new Uri("http://localhost:4317");
        })
        .Build();

    // Create activity source and meter
    var activitySource = new ActivitySource("AgentProtocol");
    var meter = new Meter("AgentProtocol");

    var messageCounter = meter.CreateCounter<long>(
        "agent.messages.sent",
        description: "Number of messages sent");

    var latencyHistogram = meter.CreateHistogram<double>(
        "agent.message.latency",
        description: "Message processing latency in milliseconds");

    // Instrument your code
    public async Task<Response> SendMessageTraced(string message)
    {
        using var activity = activitySource.StartActivity("send_message");
        activity?.SetTag("message.length", message.Length);

        var startTime = Stopwatch.GetTimestamp();
        try
        {
            var response = await _client.SendOneOffAsync(message);
            messageCounter.Add(1, new KeyValuePair<string, object>("status", "success"));
            activity?.SetStatus(ActivityStatusCode.Ok);
            return response;
        }
        catch (Exception ex)
        {
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            activity?.RecordException(ex);
            messageCounter.Add(1, new KeyValuePair<string, object>("status", "error"));
            throw;
        }
        finally
        {
            var elapsed = Stopwatch.GetElapsedTime(startTime);
            latencyHistogram.Record(elapsed.TotalMilliseconds,
                new KeyValuePair<string, object>("operation", "send_message"));
        }
    }
    ```

---

## Datadog Integration

Integrate with Datadog for comprehensive APM and monitoring.

=== "Python"

    ```python
    from ddtrace import tracer, patch
    from ddtrace.contrib.logging import patch as patch_logging
    import ddtrace

    # Enable Datadog tracing
    patch(logging=True)
    tracer.configure(
        hostname='localhost',
        port=8126,
        service='agent-protocol-client'
    )

    # Custom instrumentation
    @tracer.wrap(service='agent-client', resource='send_message')
    async def send_message(message: str):
        span = tracer.current_span()
        span.set_tag('message.length', len(message))
        span.set_tag('env', 'production')

        response = await client.send_one_off(message)

        span.set_metric('response.tokens', response.usage.total_tokens)
        return response
    ```

=== "TypeScript"

    ```typescript
    import tracer from 'dd-trace';

    // Initialize Datadog tracer
    tracer.init({
      hostname: 'localhost',
      port: 8126,
      service: 'agent-protocol-client',
      env: 'production'
    });

    // Custom instrumentation
    async function sendMessage(message: string) {
      const span = tracer.startSpan('send_message', {
        resource: 'AgentClient.sendOneOff',
        type: 'web'
      });

      span.setTag('message.length', message.length);

      try {
        const response = await client.sendOneOff(message);
        span.setTag('response.tokens', response.usage.totalTokens);
        return response;
      } catch (error) {
        span.setTag('error', error);
        throw error;
      } finally {
        span.finish();
      }
    }
    ```

=== "C#"

    ```csharp
    using Datadog.Trace;
    using Microsoft.Agents.Client;

    public async Task<Response> SendMessage(string message)
    {
        using (var scope = Tracer.Instance.StartActive("send_message"))
        {
            var span = scope.Span;
            span.ResourceName = "AgentClient.SendOneOffAsync";
            span.SetTag("message.length", message.Length);
            span.SetTag("env", "production");

            try
            {
                var response = await _client.SendOneOffAsync(message);
                span.SetTag("response.tokens", response.Usage.TotalTokens);
                return response;
            }
            catch (Exception ex)
            {
                span.SetException(ex);
                throw;
            }
        }
    }
    ```

---

## Prometheus Integration

Export metrics to Prometheus for monitoring and alerting.

=== "Python"

    ```python
    from prometheus_client import Counter, Histogram, start_http_server
    from microsoft.agents import AgentProtocolClient

    # Define metrics
    message_counter = Counter(
        'agent_messages_total',
        'Total number of messages sent',
        ['status']
    )

    message_latency = Histogram(
        'agent_message_duration_seconds',
        'Message processing duration'
    )

    # Start Prometheus metrics server
    start_http_server(8000)

    # Instrument your code
    @message_latency.time()
    async def send_message(message: str):
        try:
            response = await client.send_one_off(message)
            message_counter.labels(status='success').inc()
            return response
        except Exception:
            message_counter.labels(status='error').inc()
            raise
    ```

=== "TypeScript"

    ```typescript
    import { Registry, Counter, Histogram } from 'prom-client';
    import express from 'express';

    // Create registry
    const register = new Registry();

    // Define metrics
    const messageCounter = new Counter({
      name: 'agent_messages_total',
      help: 'Total number of messages sent',
      labelNames: ['status'],
      registers: [register]
    });

    const messageLatency = new Histogram({
      name: 'agent_message_duration_seconds',
      help: 'Message processing duration',
      registers: [register]
    });

    // Expose metrics endpoint
    const app = express();
    app.get('/metrics', async (req, res) => {
      res.set('Content-Type', register.contentType);
      res.end(await register.metrics());
    });
    app.listen(8000);

    // Instrument your code
    async function sendMessage(message: string) {
      const end = messageLatency.startTimer();
      try {
        const response = await client.sendOneOff(message);
        messageCounter.inc({ status: 'success' });
        return response;
      } catch (error) {
        messageCounter.inc({ status: 'error' });
        throw error;
      } finally {
        end();
      }
    }
    ```

=== "C#"

    ```csharp
    using Prometheus;
    using Microsoft.Agents.Client;

    // Define metrics
    private static readonly Counter MessageCounter = Metrics
        .CreateCounter("agent_messages_total", "Total messages sent",
            new CounterConfiguration { LabelNames = new[] { "status" } });

    private static readonly Histogram MessageLatency = Metrics
        .CreateHistogram("agent_message_duration_seconds",
            "Message processing duration");

    // Start metrics server
    var metricServer = new MetricServer(port: 8000);
    metricServer.Start();

    // Instrument your code
    public async Task<Response> SendMessage(string message)
    {
        using (MessageLatency.NewTimer())
        {
            try
            {
                var response = await _client.SendOneOffAsync(message);
                MessageCounter.WithLabels("success").Inc();
                return response;
            }
            catch
            {
                MessageCounter.WithLabels("error").Inc();
                throw;
            }
        }
    }
    ```

---

## AWS CloudWatch Integration

Send metrics and logs to AWS CloudWatch.

=== "Python"

    ```python
    import boto3
    from datetime import datetime

    cloudwatch = boto3.client('cloudwatch')

    def send_metric(metric_name: str, value: float, unit: str = 'Count'):
        cloudwatch.put_metric_data(
            Namespace='AgentProtocol',
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': unit,
                    'Timestamp': datetime.utcnow()
                }
            ]
        )

    # Usage
    async def send_message(message: str):
        start_time = time.time()
        try:
            response = await client.send_one_off(message)
            send_metric('MessagesSuccess', 1)
            return response
        except Exception:
            send_metric('MessagesError', 1)
            raise
        finally:
            latency = (time.time() - start_time) * 1000
            send_metric('MessageLatency', latency, 'Milliseconds')
    ```

=== "TypeScript"

    ```typescript
    import { CloudWatch } from 'aws-sdk';

    const cloudwatch = new CloudWatch();

    async function sendMetric(metricName: string, value: number, unit: string = 'Count') {
      await cloudwatch.putMetricData({
        Namespace: 'AgentProtocol',
        MetricData: [{
          MetricName: metricName,
          Value: value,
          Unit: unit,
          Timestamp: new Date()
        }]
      }).promise();
    }

    // Usage
    async function sendMessage(message: string) {
      const startTime = Date.now();
      try {
        const response = await client.sendOneOff(message);
        await sendMetric('MessagesSuccess', 1);
        return response;
      } catch (error) {
        await sendMetric('MessagesError', 1);
        throw error;
      } finally {
        const latency = Date.now() - startTime;
        await sendMetric('MessageLatency', latency, 'Milliseconds');
      }
    }
    ```

=== "C#"

    ```csharp
    using Amazon.CloudWatch;
    using Amazon.CloudWatch.Model;
    using Microsoft.Agents.Client;

    private readonly IAmazonCloudWatch _cloudWatch = new AmazonCloudWatchClient();

    private async Task SendMetric(string metricName, double value, string unit = "Count")
    {
        await _cloudWatch.PutMetricDataAsync(new PutMetricDataRequest
        {
            Namespace = "AgentProtocol",
            MetricData = new List<MetricDatum>
            {
                new MetricDatum
                {
                    MetricName = metricName,
                    Value = value,
                    Unit = unit,
                    TimestampUtc = DateTime.UtcNow
                }
            }
        });
    }

    // Usage
    public async Task<Response> SendMessage(string message)
    {
        var startTime = Stopwatch.GetTimestamp();
        try
        {
            var response = await _client.SendOneOffAsync(message);
            await SendMetric("MessagesSuccess", 1);
            return response;
        }
        catch
        {
            await SendMetric("MessagesError", 1);
            throw;
        }
        finally
        {
            var elapsed = Stopwatch.GetElapsedTime(startTime);
            await SendMetric("MessageLatency", elapsed.TotalMilliseconds, "Milliseconds");
        }
    }
    ```

---

## See Also

- [Best Practices](../best-practices/index.md)
- [Logging Guide](../logging/index.md)
- [Metrics Guide](../metrics/index.md)
- [Tracing Guide](../tracing/index.md)
- [Observability Overview](../index.md)
