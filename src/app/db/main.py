import argparse

from sqlalchemy import Engine
from sqlalchemy_utils import database_exists, create_database

from app.db import session
from app.db.models import Base


def create(engn: Engine):
    Base.metadata.create_all(engn)


def drop(engn: Engine):
    Base.metadata.drop_all(engn)


def _main(is_drop: bool = False, is_restart: bool = False):
    if is_drop:
        drop(session.engine)
    if is_restart:
        drop(session.engine)
        create(session.engine)
    else:
        create(session.engine)


def main():
    a_parser = argparse.ArgumentParser()
    a_parser.add_argument('-d', '--drop',
                          action='store_true',
                          help='Drop database')
    a_parser.add_argument('-r', '--restart',
                          action='store_true',
                          help='Restart with drop database')
    args = a_parser.parse_args()

    _main(is_drop=args.drop, is_restart=args.restart)
    # _main(is_drop=False)


if __name__ == "__main__":
    main()
