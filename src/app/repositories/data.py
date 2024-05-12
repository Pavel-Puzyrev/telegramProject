from datetime import datetime

from sqlalchemy import select, func, Integer, delete, insert, Row
from sqlalchemy.orm import aliased

from app.db import models as orm
from app.repositories.base import BaseRepository
from app.schemas import data as sch
from app.util import core


class DataRepository(BaseRepository):
    def write_json_to_db(self, jsn: bytes) -> sch.ChatModel:
        db_scheme = sch.ChatModel.model_validate_json(json_data=jsn)

        user_set = {}

        # Создаем и добавляем диалог
        tg_chat_model = orm.TgChats(**db_scheme.model_dump(exclude={'messages'}))
        self.session.add(tg_chat_model)
        self.session.flush()

        for jsn_message in db_scheme.messages:
            user_set[jsn_message.from_id] = jsn_message.from_

        for user_id, user in user_set.items():
            user_name = orm.TgUserNames(from_id=user_id, from_=user)
            self.session.add(user_name)

        self.session.flush()

        for jsn_message in db_scheme.messages:
            # Обработка сообщений
            message = orm.TgMessages(**jsn_message.model_dump(exclude={"text_entities", "from_"}),
                                     tg_chat_model_id=db_scheme.id)
            self.session.add(message)

            for text_ent in jsn_message.text_entities:
                # Обработка текста сообщений
                text_entity = orm.TgTextEntity(**text_ent.model_dump(), message_id=jsn_message.id)
                self.session.add(text_entity)

        self.session.commit()
        return db_scheme

    def get_chat_list(self):
        query = select(orm.TgChats.id)
        res = self.session.execute(query).scalars().all()
        return res

    def delete_chat(self, chat_id: int):

        self.session.delete(self.session.query(orm.TgChats).get(chat_id))
        # stmt = delete(orm.TgDialogModel).filter(orm.TgDialogModel.id == dialog_id)
        # self.session.execute(stmt)
        self.session.commit()

    def get_users(self) -> list[tuple[str, str]]:
        query = select(orm.TgUserNames.from_id, orm.TgUserNames.from_).filter(orm.TgUserNames.from_id.isnot(None))
        return [(row[0], row[1]) for row in self.session.execute(query).all()]

    def count_messages(
            self,
            user_id: str,
            date_start: datetime,
            date_end: datetime,
    ) -> int:
        """select count(m.date)
        from messages m
        join textentity t on m.id = t.message_id
        where from_ = 'Pavel P'
        group by from_"""

        m = aliased(orm.TgMessages)
        t = aliased(orm.TgTextEntity)

        query = (
            select(
                func.count(m.date)
            )
            .select_from(m)
            .join(t, m.id == t.message_id)
            .filter(m.from_id.contains(user_id))
            .filter(m.date.between(date_start, date_end))
            .group_by(m.from_id)
        )
        res = self.session.execute(query)
        result = res.scalar()
        return result

    def count_messages_per_hour(self,
                                user_id: str,
                                date_start: datetime,
                                date_end: datetime,
                                ) -> list[tuple[datetime, int]]:
        """
        with subq
         as
         (select id,
                 from_,
                 date,
                 date_trunc('hour', date)                                     as datetr,
                 count(id) over (partition by date_trunc('hour', date)) as wind
          from messages
          where from_ like 'Pavel P')
        select datetr, wind
        from subq
        group by datetr, wind
        """

        m = aliased(orm.TgMessages)

        cte = ((
                   select(
                       m.id,
                       m.from_id,
                       m.date,
                       func.date_trunc('hour', m.date).label('datetr'),
                       func.count(m.id).over(partition_by=func.date_trunc('hour', m.date)).label('wind')
                   )
                   .filter(m.from_id.contains(user_id))
                   .filter(m.date.between(date_start, date_end))
               )
               .cte('subq')
               )

        query = (
            select(
                cte.c.datetr,
                cte.c.wind,
            )
            .group_by(cte.c.datetr, cte.c.wind)
        )

        res = self.session.execute(query)
        return res.all()

    def count_messages_for_24_hours(self,
                                    user_id: str,
                                    date_start: datetime,
                                    date_end: datetime,
                                    first_month: int | None,
                                    finish_month: int | None,
                                    ) -> list[tuple[float, int]]:
        """
        select msg, count(msg)
        from (select date_part('hour', date_trunc('hour', date)) as msg
              from messages
              where from_ like '%'
                and (date_part('month', date) IN ('9','10','11')))
                 as subq
        group by msg
        order by msg
        """
        if first_month is None and finish_month is None:
            list_of_month = list(range(1, 13))
        else:
            if first_month is None:
                first_month = finish_month
            elif finish_month is None:
                finish_month = first_month
            list_of_month = core.get_month_list(first_month, finish_month)

        subq = (select(func.date_part('hour', func.date_trunc('hour', orm.TgMessages.date)).cast(Integer).label('msg'))
                .filter(orm.TgMessages.date.between(date_start, date_end))
                .filter(orm.TgMessages.from_id.like(user_id))
                .filter((func.date_part('month', orm.TgMessages.date).cast(Integer)).in_(list_of_month))
                .subquery("subq"))
        query = (select(subq.c.msg, func.count(subq.c.msg))
                 .group_by(subq.c.msg)
                 .order_by(subq.c.msg))

        res = self.session.execute(query)
        return res.all()

    def count_words_in_messages(self,
                                users_id: list[str],
                                date_start: datetime,
                                date_end: datetime,
                                ) -> tuple[int, int, float]:
        # TODO Сделать чтобы ответ был вложенный по людям
        """
        select count(t.text),
               sum(length(t.text) - length(replace(replace(t.text, '  ', ' '), ' ', ''))),
               sum(length(t.text) - length(replace(t.text, ' ', ''))) / count(t.text) as word_per_msg
        from messages m
                 join textentity t on m.id = t.message_id
        where m.type = 'message'
          and from_ = 'Pavel P'
        """
        m = aliased(orm.TgMessages)
        t = aliased(orm.TgTextEntity)

        query = (
            select(
                func.count(t.text).label("count of messages"),
                func.sum(func.length(t.text) - func.length(func.replace(func.replace(t.text, '  ', ' '), ' ', '')))
                .label("count of words"),
                (func.sum(func.length(t.text) - func.length(func.replace(func.replace(t.text, '  ', ' '), ' ', '')))
                 / func.count(t.text))
                .label('word_per_msg')
            )
            .select_from(m)
            .join(t, m.id == t.message_id)
            # .options(contains_eager(m.text_entities))
            .filter(m.type == 'message')
            .filter(m.date.between(date_start, date_end))
        )

        if users_id is not None and users_id:
            query = query.filter(m.from_id.in_(users_id))
        res = self.session.execute(query)
        return res.all()[0]
