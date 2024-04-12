import encodings
from typing import Optional, Any, Type, TypeVar, List
import pprint
from pydantic import BaseModel, Field

file = "C:\\IT\\telegramProject\\src\\banya.json"
# file = "C:\\IT\\telegramProject\\src\\result1.json"
# file = "C:\\IT\\telegramProject\\src\\derzi_v_kurse.json"


with open(file, encoding='utf-8') as f:
    jsn = f.read()


class TextItem(BaseModel):
    type: str
    text: str
    href: Optional[str] = None
    document_id: Optional[str] = None
    user_id: Optional[int] = None


class TextEntity(BaseModel):
    type: Optional[str] = None
    text: Optional[str] = None
    href: Optional[str] = None
    document_id: Optional[str] = None
    user_id: Optional[int] = None


class Answer(BaseModel):
    text: str
    voters: int
    chosen: bool


class Poll(BaseModel):
    question: str
    closed: bool
    total_voters: int
    answers: list[Answer]


class Message(BaseModel):
    id: int
    type: str
    date: str
    date_unixtime: str
    edited: Optional[str] = None
    edited_unixtime: Optional[str] = None
    from_: Optional[str] = Field(None, alias='from')
    from_id: Optional[str] = None
    reply_to_message_id: Optional[int] = None

    poll: Optional[Poll] = None  # ОПРОС
    message_id: Optional[int] = None

    forwarded_from: Optional[str] = None

    photo: Optional[str] = None
    file: Optional[str] = None
    thumbnail: Optional[str] = None
    media_type: Optional[str] = None
    mime_type: Optional[str] = None
    duration_seconds: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    sticker_emoji: Optional[str] = None
    text: str | list[str | TextItem]
    text_entities: list[TextEntity]
    # ACTIONS
    actor: Optional[str] = None
    actor_id: Optional[str] = None
    action: Optional[str] = None
    title: Optional[str] = None
    members: Optional[list[Any]] = None


class MessageSet(BaseModel):
    id: set[int]
    type: set[str]
    date: set[str]
    date_unixtime: set[str]
    edited: set[str | None]
    edited_unixtime: set[str | None]
    from_: set[str | None] = Field(alias='from')
    from_id: set[str | None]
    reply_to_message_id: set[int | None]
    poll: set[Poll | None]
    message_id: set[int | None]
    forwarded_from: set[str | None]
    photo: set[str | None]
    file: set[str | None]
    thumbnail: set[str | None]
    media_type: set[str | None]
    mime_type: set[str | None]
    duration_seconds: set[int | None]
    width: set[int | None]
    height: set[int | None]
    sticker_emoji: set[str | None]
    text: set[str | list[str | TextItem]]
    text_entities: set[list[TextEntity]]
    actor: set[str | None]
    actor_id: set[str | None]
    action: set[str | None]
    title: set[str | None]
    members: set[list[Any]]


class DialogModel(BaseModel):
    name: str
    type: str
    id: int
    messages: list[Message]


fake_db = DialogModel.model_validate_json(json_data=jsn)
print(fake_db.id)
print(fake_db.name)
print(fake_db.type)

all_messages: list[Message] = fake_db.messages


def print_field_gamut(attr_name: str, list_of_schemes: list[BaseModel]) -> str:
    # if attr_name.find("text") != -1 or attr_name.find("date") != -1 or attr_name.find("id") != -1:
    #     return None
    _ = set()
    for scheme_obj in list_of_schemes:
        # attr = None
        if attr_name is not None:
            attr = getattr(scheme_obj, attr_name)
        if attr is None:
            _.add(None)
        if not isinstance(attr, list | dict | set | tuple | BaseModel):
            _.add(attr)
        else:
            _.add(type(attr))
        # else: print("oh, fuck")
    # pprint.pprint(_)
    # print(f"{attr_name}:{_ if len(_) > 0 else " ALWAYS NONE"}")
    return f"{attr_name}:{_}"


def write_to_file(list_of_schemes: list[BaseModel]):
    file_out = "C:\\IT\\telegramProject\\src\\banya_out.json"
    with open(file_out, encoding="utf_8", mode="w") as fw:
        fw.write('{\n')
        # for attr_name in scheme_class.__fields__.keys():
        for attr_name in list_of_schemes[0].__fields__.keys():
            fw.write(f"{print_field_gamut(attr_name, list_of_schemes)},\n")
        fw.write('}')


write_to_file(all_messages)

# fake_db_dict = fake_db.model_dump()
# pprint.pprint(fake_db_dict)
