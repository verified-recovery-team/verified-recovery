from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/cpu")
def get_cpu(request: Request, namespace: str = "default"):
    prom = request.app.state.prometheus
    return prom.query_cpu(namespace=namespace)
