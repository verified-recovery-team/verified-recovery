from fastapi import APIRouter
from orchestrator.app.integrations.kubernetes import KubernetesIntegration

router = APIRouter()


k8s = KubernetesIntegration()


@router.get("/pods")
def get_pods(namespace: str = "default"):
    return k8s.list_pods(namespace=namespace)
