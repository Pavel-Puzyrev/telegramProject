import logging

from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks
from starlette import status

from app.deps.db import RepoDataDep

chat_router = APIRouter()

logger = logging.getLogger(__name__)


@chat_router.post("/write")
def write_json_to_db(file: UploadFile, data_repo: RepoDataDep, background_tasks: BackgroundTasks):
    jsn = file.file.read().decode("utf-8")
    background_tasks.add_task(data_repo.write_json_to_db, jsn)
    return {"message": "Json file is accepted for downloading in the background"}



@chat_router.get("/get-chat-list")
def get_chat_list(data_repo: RepoDataDep) \
        -> dict[str, list[int]]:
    chat_list = data_repo.get_chat_list()
    return {"chat list": chat_list}


@chat_router.delete("/delete-chat-by-id")
def delete_chat_by_id(
        data_repo: RepoDataDep,
        chat_id: int
):
    data_repo.delete_chat(chat_id)
    return {
        "status": "success",
        "data": None,
        "details": None
    }
