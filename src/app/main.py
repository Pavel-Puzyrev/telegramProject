import os

from fastapi import FastAPI

from app.api.endpoints import main_router
from app.config import settings
from app.db.main import _main
from app.util.logging import configure_loggers

# TODO: возможно приведение айди к инту и фильтрованию не-юзеров
# TODO: /write refactor output, сначала в зависимости делаешь валидацию начальную файла, с точки зрения того,
#  что это вообще джейсон формат. потом пайдентик делает валидацию данных в нём
# TODO: догрузка чатов, проверка на сущестовование и апдейт только новых данных
# TODO: универсальная ручка по получению статы по месяцам-дням недели
# ok TODO: добавить получение списка людей
# ok TODO: вывести юзеров в отдельную таблицу, соотношения с сообщениями и чатами или только сообщениями many-to-many
# ok TODO: запросы по юзер айди
# ok TODO: беграунд таск на загрузку джейсона
# ok TODO: add prefix tg_*
# ok TODO: разнести по роутерам get и DDL
# ok TODO: добавить DEL таблиц каскад
# ok TODO: dialogs -> chats


# TODO: сделать единый ответ как для матплотлиба
'''
class Value (BaseModel) :
    label: str
    value: float
    # value2: str
    # value3: str

class ChartData:
    title: str
    values: list[Value]

# 2:

class ChartArrData:
    labels: list[str]
    values: list[float]
    # values2: list[float]
    # values3: list[float]

x = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май']
y = [2, 4, 3, 1, 7]

plt.bar(x, y, label='Величина прибыли') #Параметр label позволяет задать название величины для легенды
plt.xlabel('Месяц года')
plt.ylabel('Прибыль, в млн руб.')
plt.title('Пример столбчатой диаграммы')
'''



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
