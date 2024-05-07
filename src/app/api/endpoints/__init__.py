from fastapi import APIRouter

from app.api.endpoints import data, chat

main_router = APIRouter()
main_router.include_router(chat.chat_router, prefix="/chat", tags=["chat"])
main_router.include_router(data.data_router, prefix="/data", tags=["date"])
