from fastapi import APIRouter
from app.api.routes.user_routes import router as user_router
from app.api.routes.case_routes import router as case_router

router = APIRouter()

router.include_router(user_router)
router.include_router(case_router)