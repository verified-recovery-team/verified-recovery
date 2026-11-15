import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

from kubernetes.client import CoreV1Api, AppsV1Api
from orchestrator.app.integrations.kubernetes import KubernetesIntegration


@pytest.fixture
def mock_k8s_api():
    mock_core_api = MagicMock(spec=CoreV1Api)
    mock_apps_api = MagicMock(spec=AppsV1Api)
    return mock_apps_api, mock_core_api


def test_list_pods_returns_pod_data(mock_k8s_api):
    mock_apps_api, mock_core_api = mock_k8s_api

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

    mock_core_api.list_namespaced_pod.return_value = SimpleNamespace(items=[fake_pod])
    k8s = KubernetesIntegration(core_v1_api=mock_core_api, apps_v1_api=mock_apps_api)

    result = k8s.list_pods()

    assert result == [{"name": "paymentservice", "phase": "Running", "restarts": 5}]


def test_list_pods_uses_requested_namespace(mock_k8s_api):
    mock_apps_api, mock_core_api = mock_k8s_api

    mock_core_api.list_namespaced_pod.return_value = SimpleNamespace(items=[])
    k8s = KubernetesIntegration(core_v1_api=mock_core_api, apps_v1_api=mock_apps_api)
    k8s.list_pods(namespace="payments")
    mock_core_api.list_namespaced_pod.assert_called_once_with(namespace="payments")


def test_list_pods_handles_missing_metadata(mock_k8s_api):
    mock_apps_api, mock_core_api = mock_k8s_api

    fake_pod = SimpleNamespace(
        metadata=None, status=SimpleNamespace(phase="Running", container_statuses=[])
    )
    mock_core_api.list_namespaced_pod.return_value = SimpleNamespace(items=[fake_pod])
    k8s = KubernetesIntegration(core_v1_api=mock_core_api, apps_v1_api=mock_apps_api)
    result = k8s.list_pods()

    assert result == [{"name": None, "phase": "Running", "restarts": 0}]


def test_list_pods_handles_missing_status(mock_k8s_api):
    mock_apps_api, mock_core_api = mock_k8s_api

    fake_pod = SimpleNamespace(
        metadata=SimpleNamespace(name="cartservice"), status=None
    )
    mock_core_api.list_namespaced_pod.return_value = SimpleNamespace(items=[fake_pod])
    k8s = KubernetesIntegration(core_v1_api=mock_core_api, apps_v1_api=mock_apps_api)
    result = k8s.list_pods()

    assert result == [{"name": "cartservice", "phase": None, "restarts": 0}]


# Restart test:
@pytest.mark.skip(reason="Implementation deferred")
def test_restart_deployment(mock_k8s_api):
    pass


@pytest.mark.skip(reason="Implementation deferred")
def test_restart_deployment_patch_body(mock_k8s_api):
    pass


@pytest.mark.skip(reason="Implementation deferred")
def test_restart_deployment_timestamp(mock_k8s_api):
    pass


# Scaling tests:
@pytest.mark.skip(reason="Implementation deferred")
def test_scale_deployment(mock_k8s_api):
    pass


@pytest.mark.skip(reason="Implementation deferred")
def test_scale_deployment_uses_requested_namespace(mock_k8s_api):
    pass


@pytest.mark.skip(reason="Implementation deferred")
def test_scale_deployment_allows_zero(mock_k8s_api):
    pass


@pytest.mark.skip(reason="Implementation deferred")
def test_scale_deployment_rejects_negative_replicas(mock_k8s_api):
    pass


@pytest.mark.skip(reason="Implementation deferred")
def test_scale_deployment_rejects_non_integer_replicas(mock_k8s_api):
    pass


# API failure test:
@pytest.mark.skip(reason="Implementation deferred")
def test_API_failure(mock_k8s_api):
    pass
