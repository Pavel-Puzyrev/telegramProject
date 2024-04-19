import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile
from app.schemas import data as sch
from app.deps.db import RepoDataDep

data_router = APIRouter()

logger = logging.getLogger(__name__)


@data_router.post("/write")
def write_json_to_db(file: UploadFile, data_repo: RepoDataDep):
    jsn = file.file.read().decode("utf-8")
    sch_model = data_repo.write_json_to_db(jsn)
    try:
        print(sch_model.messages[0].id)
    except Exception as e:
        print(e)


@data_router.post("/convert")
async def convert_tlg_json_to_db(file: UploadFile, data_repo: RepoDataDep):
    jsn = await file.read()

    fake_db = sch.DialogModel.model_validate_json(json_data=jsn)

    print(fake_db.id)
    print(fake_db.name)
    print(fake_db.type)

    all_messages: list[sch.Message] = fake_db.messages
    message_set = sch.MessageSet()

    def print_field_gamut(attr_name: str, list_of_schemes: list[sch.BaseModel]) -> str:
        nonlocal message_set
        # if attr_name.find("text") != -1 or attr_name.find("date") != -1 or attr_name.find("id") != -1:
        #     return None
        _ = set()
        for scheme_obj in list_of_schemes:
            # attr = None
            if attr_name is not None:
                attr = getattr(scheme_obj, attr_name)
            if attr is None:
                add_to_set = getattr(message_set, attr_name)
                add_to_set.add(None)
                setattr(message_set, attr_name, add_to_set)
                # _.add(None)
            if not isinstance(attr, list | dict | set | tuple | sch.BaseModel):
                add_to_set = getattr(message_set, attr_name)
                add_to_set.add(attr)
                setattr(message_set, attr_name, add_to_set)
                # _.add(attr)
            else:
                add_to_set = getattr(message_set, attr_name)
                add_to_set.add(type(attr))
                setattr(message_set, attr_name, add_to_set)

                # _.add(type(attr))
            # else: print("oh, fuck")
        # pprint.pprint(_)
        # print(f"{attr_name}:{_ if len(_) > 0 else " ALWAYS NONE"}")
        # return f"{attr_name}:{_}"
        return getattr(message_set, attr_name)

    def write_to_file(list_of_schemes: list[sch.BaseModel]) -> list[str]:
        string_input = []
        # for attr_name in scheme_class.__fields__.keys():
        for attr_name in list_of_schemes[0].__fields__.keys():
            string_input.append(print_field_gamut(attr_name, list_of_schemes))
        return string_input

    base_dir = Path(__file__).resolve().parent.parent.parent
    file_out = base_dir / 'resources' / 'out.json'
    list_to_write = write_to_file(all_messages)
    with open(file_out, encoding="utf_8", mode="w") as fw:
        fw.write(message_set.model_dump_json(
            by_alias=True,
            exclude={
                "poll",
                "text",
                "text_entities",
                "members",

                "id",
                "date",
                "date_unixtime",
                "edited",
                "edited_unixtime",
                "message_id",
                "reply_to_message_id",
                "forwarded_from",
            },
            indent=None
        ))

    # data_repo.convert()
    return {"OK": "Converted"}
