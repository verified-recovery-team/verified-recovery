from kubernetes import client, config
from kubernetes.client import CoreV1Api, AppsV1Api
from datetime import datetime, timezone


class KubernetesIntegration:
    def __init__(
        self, core_v1_api: CoreV1Api | None = None, apps_v1_api: AppsV1Api | None = None
    ):
        if core_v1_api is None or apps_v1_api is None:
            config.load_kube_config()

        self.core_v1_api = (
            core_v1_api if core_v1_api is not None else client.CoreV1Api()
        )
        self.apps_v1_api = (
            apps_v1_api if apps_v1_api is not None else client.AppsV1Api()
        )

    def list_pods(self, namespace: str = "default") -> list[dict]:
        pods = self.core_v1_api.list_namespaced_pod(namespace=namespace).items

        return [
            {
                "name": pod.metadata.name if pod.metadata is not None else None,
                "phase": pod.status.phase if pod.status is not None else None,
                "restarts": (
                    sum(
                        container.restart_count
                        for container in (pod.status.container_statuses or [])
                        if container is not None
                    )
                    if pod.status is not None
                    else 0
                ),
            }
            for pod in pods
        ]

    def restart_deployment(self, name: str, namespace: str = "default"):

        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": datetime.now(
                                timezone.utc
                            ).isoformat()
                        }
                    }
                }
            }
        }

        response = self.apps_v1_api.patch_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=body,
        )

        return {
            "name": response.metadata.name if response.metadata else name,
            "namespace": response.metadata.namespace
            if response.metadata
            else namespace,
            "restarted_at": (
                response.spec.template.metadata.annotations.get(
                    "kubectl.kubernetes.io/restartedAt"
                )
                if response.spec
                and response.spec.template
                and response.spec.template.metadata
                and response.spec.template.metadata.annotations
                else None
            ),
        }

    def scale_deployment(self, name: str, replicas: int, namespace: str = "default"):
        if not isinstance(replicas, int) or isinstance(replicas, bool):
            raise ValueError("replicas must be an integer.")

        if replicas < 0:
            raise ValueError("replicas cannot be negative.")

        response = self.apps_v1_api.patch_namespaced_deployment(
            name=name,
            namespace=namespace,
            body={"spec": {"replicas": replicas}},
        )

        return {
            "name": response.metadata.name if response.metadata else name,
            "namespace": response.metadata.namespace
            if response.metadata
            else namespace,
            "replicas": (
                response.spec.replicas
                if response.spec is not None and response.spec.replicas is not None
                else replicas
            ),
        }
