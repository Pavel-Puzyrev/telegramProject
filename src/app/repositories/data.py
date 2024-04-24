from datetime import datetime

from sqlalchemy import select, func, and_, any_
from sqlalchemy.orm import aliased, contains_eager

from app.repositories.base import BaseRepository
from app.schemas import data as sch
from app.db import models as orm


class DataRepository(BaseRepository):
    def write_json_to_db(self, jsn: bytes) -> sch.DialogModel:
        fake_db = sch.DialogModel.model_validate_json(json_data=jsn)

        dialog_model = orm.DialogModel(**fake_db.model_dump(
            exclude={'messages'}
        ))
        self.session.add(dialog_model)
        self.session.flush()  # ??

        dialog = self.session.get(orm.DialogModel, fake_db.id)
        messages = []
        for jsn_message in fake_db.messages:
            message = orm.Message(**jsn_message.model_dump(
                exclude={"text_entities"}
            ))
            dialog.messages.append(message)
            if jsn_message.text_entities is not None:
                text_entities = [orm.TextEntity(**t.model_dump()) for t in jsn_message.text_entities]
                message.text_entities.extend(text_entities)
            messages.append(message)
        self.session.add_all(messages)
        self.session.commit()
        return fake_db

    def count_messages(
            self,
            user_name,
            # data_start,
            # data_end,
    ):
        """select count(date)
        from messages m
        join textentity t on m.id = t.message_id
        where from_ = 'Pavel P'
        group by from_"""
        query = (
            select(
                func.count(orm.Message.date)
            )
            .filter(orm.Message.from_.contains(user_name))
            .group_by(orm.Message.from_)
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

        cte = (
            select(
                m.id,
                m.from_,
                m.date,
                func.date_trunc('hour', m.date).label('datetr'),
                func.count(m.id).over(partition_by=func.date_trunc('hour', m.date)).label('wind')
            ).filter(m.from_.contains(user_name)).filter(m.date.between(data_start, data_end))
        ).cte('subq')

        query = (
            select(
                cte.c.datetr,
                cte.c.wind,
            )
            .group_by(cte.c.datetr, cte.c.wind)
        )

        res = self.session.execute(query)
        return res.all()

    def count_word(self,
                   user_names: list[str],
                   data_start: datetime,
                   data_end: datetime,
                   ):
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
                func.count(t.text),
                func.sum(func.length(t.text) - func.length(func.replace(func.replace(t.text, '  ', ' '), ' ', ''))),
                (func.sum(func.length(t.text) - func.length(func.replace(t.text, ' ', ''))) / func.count(t.text)).label(
                    'word_per_msg')
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
        return res.all()

#
# def select_id_by_role(self, role: str) -> int:
#     # query = select(orm.Account).options(selectinload(orm.Account.role)).where(orm.Account.login == user_login)
#     query = select(orm.Role.id).where(orm.Role.role == role)
#     result = self.session.scalars(query)
#     role_id = result.first()
#     return role_id
#
