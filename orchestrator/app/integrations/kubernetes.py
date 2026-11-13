from kubernetes import client, config
from kubernetes.client import CoreV1Api


class KubernetesIntegration:
    def __init__(self, core_v1_api: CoreV1Api | None = None):
        if core_v1_api is None:
            config.load_kube_config()

            self.core_v1_api = client.CoreV1Api()
        else:
            self.core_v1_api = core_v1_api

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
