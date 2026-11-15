from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/pods")
def get_pods(request: Request, namespace: str = "default"):
    return request.app.state.kubernetes.list_pods(namespace=namespace)
