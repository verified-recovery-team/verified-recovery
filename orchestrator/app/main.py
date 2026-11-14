from contextlib import asynccontextmanager
from fastapi import FastAPI
from .api.routes import health
from .api.routes import pods
from .api.routes import cpu
from orchestrator.app.integrations.prometheus import PrometheusIntegration
from orchestrator.app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.prometheus = PrometheusIntegration(base_url=settings.prometheus_url)
    try:
        yield
    finally:
        app.state.prometheus.close()


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(pods.router)
app.include_router(cpu.router)
