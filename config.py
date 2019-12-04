from peewee import *
import os
import urllib.parse as urlparse

token = '931839019:AAEb6e9p4Rtk33SNyjYxCc3-HZo2WHuV32c'
creatorID = 144454876
creatorUsername = 'yury_zh'


if 'HEROKU' in os.environ:
    DEBUG = False
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    DATABASE = {
     'engine': 'peewee.PostgresqlDatabase',
     'name': url.path[1:],
     'user': url.username,
     'password': url.password,
     'host': url.hostname,
     'port': url.port,
 }
else:
    DEBUG = True
    DATABASE = {
        'engine': 'peewee.PostgresqlDatabase',
        'name': 'yury',
        'user': 'yury',
        'password': '12345',
        'host': 'localhost',
        'port': 5432 ,
        'threadlocals': True
    }

db = PostgresqlDatabase(
    DATABASE.get('name'),
    user=DATABASE.get('user'),
    password=DATABASE.get('password'),
    host=DATABASE.get('host'),
    port=DATABASE.get('port')
)

# db = SqliteDatabase('data.db')

ban_list = [364187993]

warningWrongDataFormat = 'Неправильный формат данных! Будь внимательней, если хочешь победить, дам тебе еще шанс'
getSurname = 'Введи свою фамилию'
welcomeMsg = 'Приветствую тебя, Отважный Эльф! Я бот игры Дарец в рамках Новогодних Праздников  на ВМК 2020! \n' \
             'Всю информацию о правилах можно найти в посте, а пока что ответь, кто ты и откуда?\n' + getSurname
getName = 'Назови свое имя'
getGroup = 'Из какой группы пришел сюда?'
getAvatar = ' Надеюсь, ты не стеснительный эльф. Тогда отправь свою фотокарточку, чтобы я мог увидеть тебя'
successfulReg = 'Формальности учтены, добро пожаловать в соревнование, скоро напишу тебе о начале... Ожидай'
startGame = 'Вперёд, помощник Санты, игра началась!'
newTarget = 'Твоя следующая цель: {} {}, {} группа.\nID жертвы: {}\nСейчас скину фото\nУдачи!'
regAgain = 'Для повтора регистрации вводи /reg'
warningWrongGroup = 'Ошибка в номере группы!\n' + regAgain
warningSomethingWentWrong = 'Что-то пошло не по плану, ошибка...\n' + regAgain
errorUnexpected = 'А тут ошибочка, тебя нет в базе. Пиши организаторам'
errorWrongTargetID = 'Проверь ID цели и пробуй еще раз'
error = 'Непредвиденная ошибка, напиши организаторам'

getTargetID = 'Введи ID следующего игрока (возьми его у твоей цели)'
killed = 'Тебя поймали! Число пойманных тобой: {}\nВ следующем году повезет больше!'
alreadyKilled = 'Тебя уже поймали! Не обманывай!'
successfulKill = 'Так держать, Великий Эльф! Сейчас выдам новую цель'
forceKill = 'Человек, которого ты ищешь, вышел из игры, так уж и быть, сейчас дам тебе нового'

congrats = 'Победа за тобой. Теперь тебе есть чем гордиться, поздравляю!'
alreadyWon = 'Игра завершена, поздравлять больше не стану'

helpMsg = '/kill – устранить эльфа'
