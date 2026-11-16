import pytest
import httpx
from urllib.parse import urlparse, parse_qs

from orchestrator.app.integrations.prometheus import PrometheusIntegration


@pytest.fixture
def prometheus_client_mock():
    captured_requests = []

    active_response = {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": [
                {
                    "metric": {
                        "namespace": "default",
                        "pod": "frontend-123",
                        "node": "minikube",
                        "container": "pod",
                    },
                    "value": [1790000000, "0.0172"],
                }
            ],
        },
    }

    active_status_code = [200]

    def mock_handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)

        return httpx.Response(
            status_code=active_status_code[0],
            json=active_response,
        )

    client = httpx.Client(
        transport=httpx.MockTransport(mock_handler),
        base_url="http://prometheus.test",
    )

    integration = PrometheusIntegration(
        base_url="http://prometheus.test",
        client=client,
    )

    def set_response(response, status_code=200):
        active_response.clear()
        active_response.update(response)
        active_status_code[0] = status_code

    setattr(integration, "_captured_requests", captured_requests)
    setattr(integration, "set_response", set_response)

    yield integration

    integration.close()


def test_query_cpu_success(prometheus_client_mock):
    results = prometheus_client_mock.query_cpu(namespace="default")

    assert len(results) == 1

    item = results[0]

    assert item["namespace"] == "default"
    assert item["pod"] == "frontend-123"
    assert item["node"] == "minikube"

    assert item["cpu_cores"] == 0.0172
    assert isinstance(item["cpu_cores"], float)

    requests = prometheus_client_mock._captured_requests

    assert len(requests) == 1

    parsed_url = urlparse(str(requests[0].url))

    assert parsed_url.path == "/api/v1/query"

    query_params = parse_qs(parsed_url.query)

    assert "query" in query_params

    promql_expr = query_params["query"][0]

    assert (
        "node_namespace_pod_container:container_cpu_usage_seconds_total:sum_rate5m"
        in promql_expr
    )
    assert 'namespace="default"' in promql_expr


def test_query_cpu_http_error(prometheus_client_mock):
    prometheus_client_mock.set_response(
        {"error": "Internal Server Error"},
        status_code=500,
    )

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        prometheus_client_mock.query_cpu(namespace="default")

    assert exc_info.value.response.status_code == 500


def test_query_cpu_api_error_status(prometheus_client_mock):
    prometheus_client_mock.set_response(
        {
            "status": "error",
            "errorType": "bad_data",
            "error": "expression parsing error: unexpected character at EOF",
        }
    )

    with pytest.raises(RuntimeError) as exc_info:
        prometheus_client_mock.query_cpu(namespace="default")

    assert "Prometheus query failed" in str(exc_info.value)
    assert "expression parsing error" in str(exc_info.value)


def test_query_cpu_malformed_sample(prometheus_client_mock):
    prometheus_client_mock.set_response(
        {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {
                            "namespace": "default",
                            "pod": "test-pod-xyz",
                            "node": "minikube",
                        },
                        "value": [1794597642.446, "not-a-number"],
                    }
                ],
            },
        }
    )

    with pytest.raises(ValueError) as exc_info:
        prometheus_client_mock.query_cpu(namespace="default")

    assert "Failed to convert metric value" in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_namespace",
    [
        "Invalid-Namespace-Uppercase",
        "-starts-with-hyphen",
        "ends-with-hyphen-",
        "has_underscores",
        "has.dots",
        "a" * 64,
        "",
    ],
)
def test_query_cpu_invalid_namespace(
    prometheus_client_mock,
    invalid_namespace,
):
    with pytest.raises(ValueError) as exc_info:
        prometheus_client_mock.query_cpu(namespace=invalid_namespace)

    assert "Invalid namespace" in str(
        exc_info.value
    ) or "Namespace must be between" in str(exc_info.value)
