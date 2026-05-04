from fastapi import APIRouter
from app.api.routes.user_routes import router as user_router
from app.api.routes.case_routes import router as case_router
from app.api.routes.access_routes import router as access_router
from app.api.routes.evidence_routes import router as evidence_router
from app.api.routes.suspect_routes import router as suspect_router
from app.api.routes.analysis_routes import router as analysis_router
from app.api.routes.contact_routes import router as contact_router

router = APIRouter()

router.include_router(user_router)
router.include_router(case_router)
router.include_router(access_router)
router.include_router(evidence_router)
router.include_router(suspect_router)
router.include_router(analysis_router)
router.include_router(contact_router)