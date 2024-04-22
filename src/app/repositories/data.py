from sqlalchemy import select, text

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
        self.session.flush()

        dialog = self.session.get(orm.DialogModel, fake_db.id)
        for n, jsn_message in enumerate(fake_db.messages):
            dialog.messages.append(orm.Message(**jsn_message.model_dump(
                exclude={"text_entities"}
            )))
            orm_message = dialog.messages[n]
            # self.session.commit()
            # message = self.session.get(orm.Message, fake_db.messages[message.id].id)
            if jsn_message.text_entities is not None:
                for t in jsn_message.text_entities:
                    orm_message.text_entities.append(orm.TextEntity(**t.model_dump()))
        self.session.commit()
        return fake_db

    # def get_user_by_id(self, user_id: int) -> orm.Account:
    #     query = (
    #         select(orm.Account).
    #         join(orm.RoleAccount, orm.RoleAccount.account_id == orm.Account.id).
    #         where(orm.Account.id == user_id)
    #     )
    #     results = self.session.scalars(query)
    #     user_out = results.first()
    #     return user_out
    #
    # def get_user_by_login(self, user_login: str) -> orm.Account:
    #     # query = select(orm.Account).options(selectinload(orm.Account.role)).where(orm.Account.login == user_login)
    #     query = select(orm.Account).where(orm.Account.login == user_login)
    #     result = self.session.scalars(query)
    #     user_out = result.first()
    #     return user_out
    #
    # def update_user(
    #         self,
    #         active_user: sch.UserOutInfo,
    #         user_for_update: sch.UserInUpdate
    # ):
    #     user_in_db = self.get_user_by_login(user_login=active_user.login)
    #
    #     for key, value in user_for_update.model_dump().items():
    #         attr = getattr(user_in_db, key)
    #         if attr != value:
    #             setattr(user_in_db, key, value)
    #
    #     self.session.commit()
    #
    #     return user_in_db
    #
    # def select_id_by_role(self, role: str) -> int:
    #     # query = select(orm.Account).options(selectinload(orm.Account.role)).where(orm.Account.login == user_login)
    #     query = select(orm.Role.id).where(orm.Role.role == role)
    #     result = self.session.scalars(query)
    #     role_id = result.first()
    #     return role_id
    #
    # def create_full_filled_user(self, usr: sch.UserFullFilled) -> (orm.Account, orm.RoleAccount):
    #     db_account_obj = orm.Account(
    #         login=usr.login,
    #         email=usr.email,
    #         psw_hash=usr.psw_hash,
    #         first_name=usr.first_name,
    #         mid_name=usr.mid_name,
    #         last_name=usr.last_name,
    #         phone=usr.phone,
    #         disabled=usr.disabled,
    #     )
    #     self.session.add(db_account_obj)
    #     self.session.flush()
    #
    #     for role_element in usr.role:
    #         db_role_account_obj = orm.RoleAccount(
    #             account_id=db_account_obj.id,
    #             role_id=self.select_id_by_role(role_element.role)
    #         )
    #         self.session.add(db_role_account_obj)
    #     self.session.commit()
    #
    #     return db_account_obj
    #
    # def fill_role_table(self):
    #     self.session.execute(text("insert into role(role) values ('1'), ('2'), ('4'), ('8')"))
    #     self.session.commit()
