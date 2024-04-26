import os

from fastapi import FastAPI

from app.api.endpoints import main_router
from app.config import settings
from app.db.main import _main
from app.util.logging import configure_loggers

configure_loggers(
    log_level=settings.log_level,
    site_logger_names=settings.site_loggers_list
)

app = FastAPI(
    title="Pavel's rest project",
    description="this project allows transfer tlg json to db and get some statistics",
    version="0.1.0",
    debug=settings.debug
)
app.include_router(main_router, prefix="/api/v1")


# @app.on_event("startup")
# async def startup_event():
#     _main(is_drop=True)
#     _main(is_drop=False)
#     ...
#     # create_fake_users(UsersRepository(session=session_maker()), n=5)


@app.get('/')
def health_check():
    return {"Server": "Up"}
