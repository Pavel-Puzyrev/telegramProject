from fastapi import APIRouter

from app.api.endpoints import data

main_router = APIRouter()
main_router.include_router(data.data_router, prefix="/tlg", tags=["tlg"])
