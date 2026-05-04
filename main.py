from fastapi import FastAPI
from app.api.routes import router
from app.database.neo4j import verify_connection, driver

app = FastAPI(title="Priora API")

app.include_router(router)

@app.on_event("startup")
async def startup():
    verify_connection()

@app.get("/")
def read_root():
    return {"message": "Priora backend is running 🚀"}

@app.on_event("shutdown")
async def shutdown():
    driver.close()