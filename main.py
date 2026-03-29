from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Priora API")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Priora backend is running 🚀"}