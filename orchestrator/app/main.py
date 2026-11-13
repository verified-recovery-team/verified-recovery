from fastapi import FastAPI
from .api.routes import health
from .api.routes import pods

app = FastAPI()

app.include_router(health.router)
app.include_router(pods.router)
