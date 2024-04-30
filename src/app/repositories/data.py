from datetime import datetime

from sqlalchemy import select, func, Integer, delete
from sqlalchemy.orm import aliased

from app.db import models as orm
from app.repositories.base import BaseRepository
from app.schemas import data as sch
from app.util import core


class DataRepository(BaseRepository):
    def write_json_to_db(self, jsn: bytes) -> sch.DialogModel:
        fake_db = sch.DialogModel.model_validate_json(json_data=jsn)

        # Создаем и добавляем диалог
        dialog_model = orm.DialogModel(**fake_db.model_dump(exclude={'messages'}))
        self.session.add(dialog_model)

        for jsn_message in fake_db.messages:
            # Обработка сообщений
            message = orm.Message(**jsn_message.model_dump(exclude={"text_entities"}), dialog_model_id=fake_db.id)
            self.session.add(message)

            for text_ent in jsn_message.text_entities:
                # Обработка текста сообщений
                text_entity = orm.TextEntity(**text_ent.model_dump(), message_id=jsn_message.id)
                self.session.add(text_entity)

        self.session.commit()
        return fake_db

    def get_dialog_list(self):
        query = select(orm.DialogModel.id)
        res = self.session.execute(query).scalars().all()
        return res

    def delete_dialog(self, dialog_id:int):

        self.session.delete(self.session.query(orm.DialogModel).get(dialog_id))
        # stmt = delete(orm.DialogModel).filter(orm.DialogModel.id == dialog_id)
        # self.session.execute(stmt)
        self.session.commit()

    def get_users(self) -> list[str]:
        query = select(orm.Message.from_).distinct(orm.Message.from_).filter(orm.Message.from_.isnot(None))
        return self.session.scalars(query).all()

    def count_messages(
            self,
            user_name: str,
            data_start: datetime,
            data_end: datetime,
    ) -> int:
        """select count(m.date)
        from messages m
        join textentity t on m.id = t.message_id
        where from_ = 'Pavel P'
        group by from_"""

        m = aliased(orm.Message)
        t = aliased(orm.TextEntity)

        query = (
            select(
                func.count(m.date)
            )
            .select_from(m)
            .join(t, m.id == t.message_id)
            .filter(m.from_.contains(user_name))
            .filter(m.date.between(data_start, data_end))
            .group_by(m.from_)
        )
        res = self.session.execute(query)
        result = res.scalar()
        return result

    def count_messages_per_hour(self,
                                user_name: str,
                                data_start: datetime,
                                data_end: datetime,
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

        m = aliased(orm.Message)

        cte = ((
                   select(
                       m.id,
                       m.from_,
                       m.date,
                       func.date_trunc('hour', m.date).label('datetr'),
                       func.count(m.id).over(partition_by=func.date_trunc('hour', m.date)).label('wind')
                   )
                   .filter(m.from_.contains(user_name))
                   .filter(m.date.between(data_start, data_end))
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
                                    user_name: str,
                                    data_start: datetime,
                                    data_end: datetime,
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

        subq = (select(func.date_part('hour', func.date_trunc('hour', orm.Message.date)).cast(Integer).label('msg'))
                .filter(orm.Message.date.between(data_start, data_end))
                .filter(orm.Message.from_.like(user_name))
                .filter((func.date_part('month', orm.Message.date).cast(Integer)).in_(list_of_month))
                .subquery("subq"))
        query = (select(subq.c.msg, func.count(subq.c.msg))
                 .group_by(subq.c.msg)
                 .order_by(subq.c.msg))

        res = self.session.execute(query)
        return res.all()

    def count_words_in_messages(self,
                                user_names: list[str],
                                data_start: datetime,
                                data_end: datetime,
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
        m = aliased(orm.Message)
        t = aliased(orm.TextEntity)

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
            .filter(m.date.between(data_start, data_end))
        )

        if user_names is not None and user_names:
            query = query.filter(m.from_.in_(user_names))
        res = self.session.execute(query)
        return res.all()[0]
