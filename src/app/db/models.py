from __future__ import annotations

import datetime
from typing import Annotated

from sqlalchemy import Integer, ForeignKey, BigInteger, UniqueConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship

intpk = Annotated[int, mapped_column(Integer, primary_key=True)]


class Base(DeclarativeBase):
    pass


class TgChats(Base):
    __tablename__ = 'tg_chats'
    id: Mapped[intpk]
    name: Mapped[str]
    type: Mapped[str]

    tg_messages: Mapped[list["TgMessages"]] = relationship(
        back_populates="tg_chat",
        cascade="all,delete",
        passive_deletes=True,
    )


class TgMessages(Base):
    __tablename__ = 'tg_messages'
    id: Mapped[intpk]
    type: Mapped[str]
    date: Mapped[datetime.datetime]
    edited: Mapped[datetime.datetime | None]
    # from_: Mapped[str | None]
    from_id: Mapped[str | None] = mapped_column(String, ForeignKey('tg_user_names.from_id', ondelete='CASCADE'))
    reply_to_message_id: Mapped[int | None]
    message_id: Mapped[int | None]
    media_type: Mapped[str | None]
    mime_type: Mapped[str | None]
    actor: Mapped[str | None]
    actor_id: Mapped[str | None]
    action: Mapped[str | None]
    title: Mapped[str | None]
    tg_chat_model_id: Mapped[int] = mapped_column(Integer, ForeignKey('tg_chats.id', ondelete='CASCADE'))

    tg_chat: Mapped["TgChats"] = relationship(
        back_populates="tg_messages",
    )

    tg_text_entities: Mapped[list["TgTextEntity"]] = relationship(
        back_populates="tg_messages",
        cascade="all,delete",
        passive_deletes=True,
    )
    # date_unixtime: Mapped[str]
    # edited_unixtime: Mapped[str | None]
    # poll_id: Mapped[int | None] = mapped_column(ForeignKey('polls.id'))
    # forwarded_from: Mapped[str | None]
    # photo: Mapped[str | None]
    # file: Mapped[str | None]
    # thumbnail: Mapped[str | None]
    # duration_seconds: Mapped[int | None]
    # width: Mapped[int | None]
    # height: Mapped[int | None]
    # sticker_emoji: Mapped[str | None]
    # text: Mapped[str | None]  # Note: complex JSON structure might need handling
    # text_entities
    # members: Mapped[list[str]] = mapped_column(...)
    # dialog_model_id: Mapped[int] = mapped_column(Integer, ForeignKey('dialogs.id'), primary_key=True)
    # Relationships
    # poll: Mapped[Poll] = relationship(back_populates="tg_messages")


class TgTextEntity(Base):
    __tablename__ = "tg_textentity"
    id: Mapped[intpk]
    type: Mapped[str | None]
    text: Mapped[str | None]
    href: Mapped[str | None]
    document_id: Mapped[str | None]
    user_id: Mapped[int | None] = mapped_column(BigInteger)
    message_id: Mapped[int] = mapped_column(ForeignKey('tg_messages.id', ondelete='CASCADE'))

    tg_messages: Mapped["TgMessages"] = relationship(
        back_populates="tg_text_entities"
    )


class TgUserNames(Base):
    __tablename__ = "tg_user_names"
    id: Mapped[intpk]
    from_: Mapped[str | None]
    from_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    tg_messages: Mapped[list["TgMessages"]] = relationship()

# class Poll(Base):
#     __tablename__ = 'polls'
#     id: Mapped[intpk]
#     question: Mapped[str]
#     closed: Mapped[bool]
#     total_voters: Mapped[int]
#
#     answers: Message[Answer] = relationship(back_populates="poll")
#

# class Answer(Base):
#     __tablename__ = 'answers'
#     id: Mapped[intpk]
#     text: Mapped[str]
#     voters: Mapped[int]
#     chosen: Mapped[bool]
#     poll_id: Mapped[int] = mapped_column(ForeignKey('polls.id'))

# poll: Mapped[Poll] = relationship(back_populates="answers")
