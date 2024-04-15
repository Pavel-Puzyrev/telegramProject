import pathlib
from typing import Optional, Any

from pydantic import BaseModel, Field

file = "resources/banya.json"
# file = "/app/resources/result1.json"
# file = "/app/resources/derzi_v_kurse.json"


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
    id: set[int] = set()
    type: set[str] = set()
    date: set[str] = set()
    date_unixtime: set[str] = set()
    edited: set[str | None] = set()
    edited_unixtime: set[str | None] = set()
    from_: set[str | None] = Field(default=set(), alias='from')
    from_id: set[str | None] = set()
    reply_to_message_id: set[int | None] = set()
    poll: set[Poll | None] = set()
    message_id: set[int | None] = set()
    forwarded_from: set[str | None] = set()
    photo: set[str | None] = set()
    file: set[str | None] = set()
    thumbnail: set[str | None] = set()
    media_type: set[str | None] = set()
    mime_type: set[str | None] = set()
    duration_seconds: set[int | None] = set()
    width: set[int | None] = set()
    height: set[int | None] = set()
    sticker_emoji: set[str | None] = set()
    text: set[str | list[str | TextItem]] = set()
    text_entities: set[list[TextEntity]] = set()
    actor: set[str | None] = set()
    actor_id: set[str | None] = set()
    action: set[str | None] = set()
    title: set[str | None] = set()
    members: set[list[str | None]] = set()


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
message_set = MessageSet()


def print_field_gamut(attr_name: str, list_of_schemes: list[BaseModel]) -> str:
    global message_set
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
        if not isinstance(attr, list | dict | set | tuple | BaseModel):
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


def write_to_file(list_of_schemes: list[BaseModel]) -> list[str]:
    string_input = []
    # for attr_name in scheme_class.__fields__.keys():
    for attr_name in list_of_schemes[0].__fields__.keys():
        string_input.append(print_field_gamut(attr_name, list_of_schemes))
    return string_input


file_out = "resources/banya_out.json"
list_to_write = write_to_file(all_messages)
with open(file_out, encoding="utf_8", mode="w") as fw:
    # fw.write("\n".join(list_to_write))
    # fw.write(message_set.model_dump(by_alias=True, exclude_none=True))
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

# fake_db_dict = fake_db.model_dump()
# pprint.pprint(fake_db_dict)
