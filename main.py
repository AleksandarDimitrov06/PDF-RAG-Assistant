from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.router import router
from api.dependencies import AppDependencies


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.dependencies = AppDependencies()
    yield
    app.state.dependencies = None

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI server is running!"}