from fastapi import FastAPI
from api.router import router

app = FastAPI()

app.include_router(router)

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI server is running!"}