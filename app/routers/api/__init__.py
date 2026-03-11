from fastapi import APIRouter

from app.routers.api.departments import router as department_router


__all__ = ["api_router"]

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(department_router, prefix="/departments", tags=["departments"])
