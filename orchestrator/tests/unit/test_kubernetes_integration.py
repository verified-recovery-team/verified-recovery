import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

from kubernetes.client import CoreV1Api
from orchestrator.app.integrations.kubernetes import KubernetesIntegration


@pytest.fixture
def mock_k8s_api():
    api = MagicMock(spec=CoreV1Api)
    return api


def test_list_pods_returns_pod_data(mock_k8s_api):
    fake_pod = SimpleNamespace(
        metadata=SimpleNamespace(name="paymentservice"),
        status=SimpleNamespace(
            phase="Running",
            container_statuses=[
                SimpleNamespace(restart_count=2),
                SimpleNamespace(restart_count=3),
            ],
        ),
    )

    mock_k8s_api.list_namespaced_pod.return_value = SimpleNamespace(items=[fake_pod])
    k8s = KubernetesIntegration(core_v1_api=mock_k8s_api)

    result = k8s.list_pods()

    assert result == [{"name": "paymentservice", "phase": "Running", "restarts": 5}]


def test_list_pods_uses_requested_namespace(mock_k8s_api):
    mock_k8s_api.list_namespaced_pod.return_value = SimpleNamespace(items=[])
    k8s = KubernetesIntegration(core_v1_api=mock_k8s_api)
    k8s.list_pods(namespace="payments")
    mock_k8s_api.list_namespaced_pod.assert_called_once_with(namespace="payments")


def test_list_pods_handles_missing_metadata(mock_k8s_api):
    fake_pod = SimpleNamespace(
        metadata=None, status=SimpleNamespace(phase="Running", container_statuses=[])
    )
    mock_k8s_api.list_namespaced_pod.return_value = SimpleNamespace(items=[fake_pod])
    k8s = KubernetesIntegration(core_v1_api=mock_k8s_api)
    result = k8s.list_pods()

    assert result == [{"name": None, "phase": "Running", "restarts": 0}]


def test_list_pods_handles_missing_status(mock_k8s_api):
    fake_pod = SimpleNamespace(
        metadata=SimpleNamespace(name="cartservice"), status=None
    )
    mock_k8s_api.list_namespaced_pod.return_value = SimpleNamespace(items=[fake_pod])
    k8s = KubernetesIntegration(core_v1_api=mock_k8s_api)
    result = k8s.list_pods()

    assert result == [{"name": "cartservice", "phase": None, "restarts": 0}]
