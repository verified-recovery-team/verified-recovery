from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field, StrictInt
from kubernetes.client.exceptions import ApiException


router = APIRouter(prefix="/deployments", tags=["deployments"])


class ScaleRequest(BaseModel):
    replicas: StrictInt = Field(..., description="Desired number of replicas")


@router.post("/{namespace}/{name}/restart")
def restart_deployment(request: Request, namespace: str, name: str):
    k8s = request.app.state.kubernetes
    try:
        result = k8s.restart_deployment(name=name, namespace=namespace)
        return {"status": "success", "data": result}
    except ApiException as e:
        status_code = (
            e.status if e.status is not None else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(
            status_code=status_code, detail=e.reason or "Kubernetes API error"
        )


@router.patch("/{namespace}/{name}/scale")
def scale_deployment(namespace: str, name: str, body: ScaleRequest, request: Request):
    if body.replicas < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Replica count cannot be negative.",
        )

    k8s = request.app.state.kubernetes
    try:
        result = k8s.scale_deployment(
            name=name, namespace=namespace, replicas=body.replicas
        )
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ApiException as e:
        status_code = (
            e.status if e.status is not None else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(
            status_code=status_code, detail=e.reason or "Kubernetes API error"
        )
