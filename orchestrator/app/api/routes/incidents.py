from fastapi import APIRouter, Request, HTTPException, Query, status
from pydantic import BaseModel


router = APIRouter(prefix="/incidents", tags=["incidents"])


class IncidentCreate(BaseModel):
    namespace: str
    resource_type: str
    resource_name: str
    trigger: str
    status: str
    diagnosis: str | None = None
    action: str | None = None
    details: dict | None = None


@router.post("", status_code=status.HTTP_201_CREATED)
def create_incident(body: IncidentCreate, request: Request):
    return request.app.state.incident_store.create_incident(**body.model_dump())


@router.get("")
def list_incidents(
    request: Request,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    return request.app.state.incident_store.list_incidents(limit=limit, offset=offset)


@router.get("/{incident_id}")
def get_incident(incident_id: int, request: Request):
    incident = request.app.state.incident_store.get_incident(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident
