from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import session_maker
from app.repositories import data as user_repo


def get_db():
    sess = session_maker()
    try:
        yield sess
    finally:
        sess.close()


SessionDep = Annotated[Session, Depends(get_db)]


def get_user_repo(session: SessionDep):
    return user_repo.DataRepository(session)


RepoDataDep = Annotated[user_repo.DataRepository, Depends(get_user_repo)]
