from fastapi import FastAPI
from kubernetes import client, config

app = FastAPI()


config.load_kube_config()
v1 = client.CoreV1Api()


@app.get("/health")
def get_health():
    return {"status": "ok"}



@app.get("/pods")
def get_pods(namespace: str = "default"):
    pods = v1.list_namespaced_pod(namespace=namespace).items

    return [
        {
            "name": pod.metadata.name,
            "phase": pod.status.phase,
            "restarts": sum(
                container.restart_count for container in (pod.status.container_statuses or [])
            ),
        }
        for pod in pods
    ]
