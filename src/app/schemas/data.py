from typing import Optional, Any

from pydantic import BaseModel, Field


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
