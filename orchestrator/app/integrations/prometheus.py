import httpx
import re

NAMESPACE_REGEX = re.compile(r"[a-z0-9]([-a-z0-9]*[a-z0-9])?")


class PrometheusIntegration:
    def __init__(self, base_url: str, timeout=5.0, client: httpx.Client | None = None):
        if client is None:
            self.client = httpx.Client(base_url=base_url, timeout=timeout)
        else:
            self.client = client

    def query_cpu(self, namespace: str = "default") -> list[dict]:
        if not isinstance(namespace, str):
            raise ValueError("Namespace must be a string.")

        if not namespace or len(namespace) > 63:
            raise ValueError("Namespace must be between 1 and 63 characters long.")

        if not re.fullmatch(NAMESPACE_REGEX, namespace):
            raise ValueError(
                f"Invalid namespace '{namespace}'. Kubernetes namespace names must consist of "
                "lowercase alphanumeric characters or '-', and start/end with an alphanumeric character."
            )

        promql = f'node_namespace_pod_container:container_cpu_usage_seconds_total:sum_rate5m{{namespace="{namespace}"}}'

        response = self.client.get(
            "/api/v1/query",
            params={"query": promql},
        )
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            error_message = data.get("error", "Unknown Prometheus error")
            raise RuntimeError(f"Prometheus query failed: {error_message}")

        results = data.get("data", {}).get("result", [])

        parsed_data = []

        for item in results:
            metric = item.get("metric", {})
            value_array = item.get("value")
            if not isinstance(value_array, list) or len(value_array) < 2:
                raise ValueError(
                    f"Malformed or missing sample value in Prometheus response: {item}"
                )

            try:
                cpu_cores = float(value_array[1])
            except (TypeError, ValueError) as e:
                raise ValueError(
                    f"Failed to convert metric value '{value_array[1]}' to float: {e}"
                ) from e

            parsed_data.append(
                {
                    "namespace": metric.get("namespace"),
                    "pod": metric.get("pod"),
                    "node": metric.get("node"),
                    "cpu_cores": cpu_cores,
                }
            )

        return parsed_data

    def close(self):
        self.client.close()
