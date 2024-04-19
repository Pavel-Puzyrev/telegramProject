import argparse

from sqlalchemy import Engine
from sqlalchemy_utils import database_exists, create_database

from app.db import session
from app.db.models import Base


def create(engn: Engine):
    Base.metadata.create_all(engn)


def drop(engn: Engine):
    Base.metadata.drop_all(engn)


def _main(is_drop: bool = False):
    if is_drop:
        drop(session.engine)
    else:
        create(session.engine)


def main():
    a_parser = argparse.ArgumentParser()
    a_parser.add_argument('--drop', '-d',
                          action='store_true',
                          help='Drop database')
    args = a_parser.parse_args()

    _main(is_drop=args.drop)
    # _main(is_drop=False)


if __name__ == "__main__":
    main()
