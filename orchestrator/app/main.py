from contextlib import asynccontextmanager
from fastapi import FastAPI

from .api.routes import health, pods, cpu, deployments, incidents

from orchestrator.app.integrations.prometheus import PrometheusIntegration
from orchestrator.app.integrations.kubernetes import KubernetesIntegration
from orchestrator.app.integrations.incident_store import IncidentStore
from orchestrator.app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.prometheus = PrometheusIntegration(base_url=settings.prometheus_url)
    app.state.kubernetes = KubernetesIntegration()

    app.state.incident_store = IncidentStore(
        database_path=settings.incident_database_path
    )
    app.state.incident_store.initialize()

    try:
        yield
    finally:
        app.state.prometheus.close()


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(pods.router)
app.include_router(cpu.router)
app.include_router(deployments.router)
app.include_router(incidents.router)
