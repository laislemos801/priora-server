from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.database.neo4j import verify_connection, ensure_constraints, driver

app = FastAPI(title="Priora API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup():
    verify_connection()
    ensure_constraints()

@app.get("/")
def read_root():
    return {"message": "Priora backend is running 🚀"}

@app.on_event("shutdown")
async def shutdown():
    driver.close()
