import logging

from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks
from starlette import status

from app.deps.db import RepoDataDep

chat_router = APIRouter()

logger = logging.getLogger(__name__)


@chat_router.post("/write")
def write_json_to_db(file: UploadFile, data_repo: RepoDataDep, background_tasks: BackgroundTasks):
    """
    Загружает JSON файл фоновой задачей и проверяет его валидность.
    """
    jsn = file.file.read().decode("utf-8")
    if data_repo.verify_json(jsn):
        background_tasks.add_task(data_repo.write_json_to_db_new, jsn)
        return {"message": "Json file is accepted for downloading in the background"}
    else:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
                            , detail="Предоставленный файл не является валидным JSON")



@chat_router.get("/get-chat-list")
def get_chat_list(data_repo: RepoDataDep) \
        -> dict[str, list[int]]:
    """
    Возвращает список идентификаторов чатов
    """
    chat_list = data_repo.get_chat_list()
    return {"chat list": chat_list}


@chat_router.delete("/delete-chat-by-id", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_by_id(
        data_repo: RepoDataDep,
        chat_id: int
):
    """
    Удаляет чат по его идентификатору
    """
    data_repo.delete_chat(chat_id)

