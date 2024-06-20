import logging
from datetime import datetime
from typing import Any, Annotated

from fastapi import APIRouter, Depends, Query

from app.deps.db import RepoDataDep
from app.schemas import data as sch

data_router = APIRouter()

logger = logging.getLogger(__name__)


@data_router.get("/get-users")
def get_users(data_repo: RepoDataDep) -> dict[str, list[tuple[str, str]]]:
    """
    Возвращает список всех пользователей.
    """
    return {"users": data_repo.get_users()}


@data_router.get("/count-messages")
def count_messages(
        data_repo: RepoDataDep,
        user_id:str = "user576909227",
        date_start: datetime = datetime.fromtimestamp(0),
        date_end: datetime = datetime.now(),
) -> dict[str, int]:
    count_of_user_messages = data_repo.count_messages(user_id,date_start,date_end)
    return {"count": count_of_user_messages}


@data_router.get("/count-messages-per-hour")
def count_messages_per_hour(
        data_repo: RepoDataDep,
        user_id: str = "user576909227",
        date_start: datetime = datetime.fromtimestamp(0),
        date_end: datetime = datetime.now(),
) -> dict[str, list[sch.CountMessagesByUserOut]]:
    count_of_messages_per_hour = data_repo.count_messages_per_hour(
        user_id,
        date_start,
        date_end,
    )
    list_of_count_messages_per_hour = []
    for row in count_of_messages_per_hour:
        list_of_count_messages_per_hour.append(sch.CountMessagesByUserOut(timestamp=row[0], count=row[1]))
    return {"Messages per hours": list_of_count_messages_per_hour}


@data_router.put("/count-word")
def count_words_in_messages(body: Annotated[sch.CountWordsInMessagesIn, Depends()],
                            data_repo: RepoDataDep) -> dict[str, Any]:
    tuple_with_count_msg_wrds_wrd_per_msg = data_repo.count_words_in_messages(
        **body.model_dump()
    )
    return {
        "count of messages": tuple_with_count_msg_wrds_wrd_per_msg[0],
        "count of words": tuple_with_count_msg_wrds_wrd_per_msg[1],
        "word_per_msg": round(tuple_with_count_msg_wrds_wrd_per_msg[2], 2)
    }


@data_router.get("/count-messages-for-24-hours")
def count_messages_for_24_hours(
        data_repo: RepoDataDep,
        user_id: str = "user576909227",
        date_start: datetime = datetime.fromtimestamp(0),
        date_end: datetime = datetime.now(),
        first_month: Annotated[int | None, Query(ge=1, le=12)] = None,
        finish_month: Annotated[int | None, Query(ge=1, le=12)] = None,
) -> dict[float, int]:
    cnt = data_repo.count_messages_for_24_hours(
        user_id,
        date_start,
        date_end,
        first_month,
        finish_month,
    )
    return dict(cnt)
