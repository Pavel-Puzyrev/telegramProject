import logging
from datetime import datetime
from typing import Any, Annotated

from fastapi import APIRouter, UploadFile, Depends, HTTPException, Query
from starlette import status

from app.deps.db import RepoDataDep
from app.schemas import data as sch

data_router = APIRouter()

logger = logging.getLogger(__name__)

# TODO: добавить получение списка людей
# TODO: сделать единый ответ как для матплотлиба
'''
x = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май']
y = [2, 4, 3, 1, 7]

plt.bar(x, y, label='Величина прибыли') #Параметр label позволяет задать название величины для легенды
plt.xlabel('Месяц года')
plt.ylabel('Прибыль, в млн руб.')
plt.title('Пример столбчатой диаграммы')
'''


# TODO: добавить DEL таблиц каскад
# TODO: разнести по роутерам get и DDL


@data_router.post("/write")
def write_json_to_db(file: UploadFile, data_repo: RepoDataDep):
    jsn = file.file.read().decode("utf-8")
    try:
        data_repo.write_json_to_db(jsn)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={
                                "status": "error",
                                "data": None,
                                "details": e
                            })


@data_router.get("/get-dialog-list")
def get_dialog_list(data_repo: RepoDataDep) \
        -> dict[str, list[int]]:
    dialog_list = data_repo.get_dialog_list()
    return {"dialog list": dialog_list}


@data_router.delete("/delete-dialog-by-id")
def delete_dialog_by_id(
        data_repo: RepoDataDep,
        dialog_id:int
):
    data_repo.delete_dialog(dialog_id)
    return {
        "status": "success",
        "data": None,
        "details": None
    }


@data_router.get("/get-users")
def get_users(data_repo: RepoDataDep) -> dict[str, list[str]]:
    return {"users": data_repo.get_users()}


@data_router.get("/count-messages")
def count_messages(
        data_repo: RepoDataDep,
        user_name="Pavel P",
        data_start: datetime = datetime.fromtimestamp(0),
        data_end: datetime = datetime.now(),
) -> dict[str, int]:
    cnt = data_repo.count_messages(
        user_name,
        data_start,
        data_end,
    )
    return {"count": cnt}


@data_router.get("/count-messages-per-hour")
def count_messages_per_hour(
        data_repo: RepoDataDep,
        user_name: str = "Pavel P",
        data_start: datetime = datetime.fromtimestamp(0),
        data_end: datetime = datetime.now(),
) -> list[sch.CountMessagesByUserOut]:
    cnt = data_repo.count_messages_per_hour(
        user_name,
        data_start,
        data_end,
    )
    res = []
    for row in cnt:
        res.append(sch.CountMessagesByUserOut(timestamp=row[0], count=row[1]))
    return res


@data_router.put("/count-word")
def count_words_in_messages(body: Annotated[sch.CountWordsInMessagesIn, Depends()],
                            data_repo: RepoDataDep) -> dict[str, Any]:
    res = data_repo.count_words_in_messages(
        **body.model_dump()
    )
    return {"count of messages": res[0],
            "count of words": res[1],
            "word_per_msg": round(res[2], 2)
            }


@data_router.get("/count-messages-for-24-hours")
def count_messages_for_24_hours(
        data_repo: RepoDataDep,
        user_name: str,
        data_start: datetime = datetime.fromtimestamp(0),
        data_end: datetime = datetime.now(),
        first_month: Annotated[int | None, Query(ge=1, le=12)] = None,
        finish_month: Annotated[int | None, Query(ge=1, le=12)] = None,
) -> dict[float, int]:
    cnt = data_repo.count_messages_for_24_hours(
        user_name,
        data_start,
        data_end,
        first_month,
        finish_month,
    )
    res = dict()
    for i in cnt:
        res.update({i[0]: i[1]})
    return res

# @data_router.post("/convert")
# async def convert_tlg_json_to_db(file: UploadFile, data_repo: RepoDataDep):
#     jsn = await file.read()
#
#     fake_db = sch.DialogModel.model_validate_json(json_data=jsn)
#
#     print(fake_db.id)
#     print(fake_db.name)
#     print(fake_db.type)
#
#     all_messages: list[sch.Message] = fake_db.messages
#     message_set = sch.MessageSet()
#
#     def print_field_gamut(attr_name: str, list_of_schemes: list[sch.BaseModel]) -> str:
#         nonlocal message_set
#         # if attr_name.find("text") != -1 or attr_name.find("date") != -1 or attr_name.find("id") != -1:
#         #     return None
#         _ = set()
#         for scheme_obj in list_of_schemes:
#             # attr = None
#             if attr_name is not None:
#                 attr = getattr(scheme_obj, attr_name)
#             if attr is None:
#                 add_to_set = getattr(message_set, attr_name)
#                 add_to_set.add(None)
#                 setattr(message_set, attr_name, add_to_set)
#                 # _.add(None)
#             if not isinstance(attr, list | dict | set | tuple | sch.BaseModel):
#                 add_to_set = getattr(message_set, attr_name)
#                 add_to_set.add(attr)
#                 setattr(message_set, attr_name, add_to_set)
#                 # _.add(attr)
#             else:
#                 add_to_set = getattr(message_set, attr_name)
#                 add_to_set.add(type(attr))
#                 setattr(message_set, attr_name, add_to_set)
#
#                 # _.add(type(attr))
#             # else: print("oh, fuck")
#         # pprint.pprint(_)
#         # print(f"{attr_name}:{_ if len(_) > 0 else " ALWAYS NONE"}")
#         # return f"{attr_name}:{_}"
#         return getattr(message_set, attr_name)
#
#     def write_to_file(list_of_schemes: list[sch.BaseModel]) -> list[str]:
#         string_input = []
#         # for attr_name in scheme_class.__fields__.keys():
#         for attr_name in list_of_schemes[0].__fields__.keys():
#             string_input.append(print_field_gamut(attr_name, list_of_schemes))
#         return string_input
#
#     base_dir = Path(__file__).resolve().parent.parent.parent
#     file_out = base_dir / 'resources' / 'out.json'
#     list_to_write = write_to_file(all_messages)
#     with open(file_out, encoding="utf_8", mode="w") as fw:
#         fw.write(message_set.model_dump_json(
#             by_alias=True,
#             exclude={
#                 "poll",
#                 "text",
#                 "text_entities",
#                 "members",
#
#                 "id",
#                 "date",
#                 "date_unixtime",
#                 "edited",
#                 "edited_unixtime",
#                 "message_id",
#                 "reply_to_message_id",
#                 "forwarded_from",
#             },
#             indent=None
#         ))
#
#     # data_repo.convert()
#     return {"OK": "Converted"}
