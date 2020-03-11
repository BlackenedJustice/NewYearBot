from peewee import *
import os
import urllib.parse as urlparse

token = '931839019:AAGU8mR-9CUWLU7SvAMNQBlM4wn5EJ5XB-c'
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

warningWrongDataFormat = '⚠️WARNING⚠️\nОбнаружен несанкционированный доступ.\nПовторите подключение... '
getSurname = '⚠️WARNING⚠️\nЛаборатория 07: произошёл сбой!\n\nВнимание! В результате сбоя аппаратуры произошло...\n' \
             'Создание многих клонов...\nБез их устранения возвращение домой невозможно...\nНеобходимо провести ' \
             'идентификацию...\nВаша фамилия...'
welcomeMsg = 'Несколько дней назад известный ученый, твой наставник, изобрел машину времени, и первое её ' \
             'тестирование он решил провести на тебе. Однако произошел сбой аппаратуры, вследствие чего в прошлом в ' \
             'один момент было создано большое количество твоих клонов, каждый из которых думает, что он настоящий. ' \
             'Вернуться в настоящее сможет только один, однако их одновременное существование разрушает ' \
             'пространственно-временной континуум, поэтому нужно уничтожить всех клонов любой ценой.'
getName = 'Имя...'
getGroup = 'Группа...'
getAvatar = 'Фото...'
successfulReg = 'Идентификация прошла успешно...\nРекомендовано посмотреть правила\nЧтобы ознакомитсья с ними, ' \
                'введи команду /rules'
startGame = 'Игра началась!\nСкорее узнай одного из своих клонов...'
newTarget = 'Идет поиск ближайших клонов...\n{}...\nБлижайшая цель: {} {}\nID: {}\nГруппа:{}'
regAgain = 'Для повтора регистрации вводи /reg'
warningWrongGroup = 'Ошибка в номере группы!\n' + regAgain
warningSomethingWentWrong = 'Что-то пошло не по плану, ошибка...\n' + regAgain
errorUnexpected = 'Клон не зарегистрирован. Свяжись с организаторами'
errorWrongTargetID = 'Проверь ID клона и пробуй еще раз'
error = '⚠️WARNING⚠️\n️Непредвиденная ошибка, напиши организаторам'

getTargetID = 'Введи ID следующего клона (возьми его у твоей цели)'
killed = 'Ты был близок...\nВпрочем, вдруг ты не настоящий?\nВ следующий раз докажешь свою подлинность.\n' \
         'Число устраненных клонов: {}'
alreadyKilled = 'Тебя уже устранили! Не обманывай!'
successfulKill = 'Клон устранен'
forceKill = 'Клон самоустранился'

congrats = 'Клоны успешно устранены! Ты доказал свою подлинность'
alreadyWon = 'Игра завершена, поздравлять больше не стану'

helpMsg = '/kill – устранить клона\n/rules - посмотреть правила'
adminHelp = '/force_kill <username> - убить игрока заранее (ВНИМАНИЕ! @None - не юзернейм!)\n' \
            '/show_cycle - показать цикл игры\n/everyone - отправить сообщение всем пользователям\n' \
            '/wall - отправить сообщение админам\n/get_photo <username> - получить фото человека\n' \
            '/show_players - показать зарегистрированных игроков\n/say <tg_id> <msg> - send message to user'

motiveMessages = [
    'Ты на шаг ближе к дому, но вокруг тебя все ещё полно врагов',
    'Осталось не так много, ты сможешь вернуться домой',
    'Еще осталось несколько клонов, давай поднажми',
    'Еще слишком много клонов, поторопись',
    'Хорошо идешь, возможно, ты и есть настоящий'
]

rules = '️⚠️ЧИТАТЬ ДО КОНЦА⚠️\n' \
        '️Руководство к игре:\n1) Получи свой первый заказ( ID жертвы) у бота\n2) Выследи клона, указанного в ' \
        'заказе\n3) Захлопни слэп-браслет на руке или ноге своей жертвы и скажи ключевую фразу: «Ещё одним клоном ' \
        'меньше». \n4) Устранение без предъявления активного заказа, а также без ключевой фразы не считается ' \
        'совершенным \n5) Оставь браслет на устраненном клоне, чтобы клон не мог больше играть.\n6) Во время своих ' \
        'поисков необходимо всегда иметь при себе активный заказ, чтобы передать его в случае своего устранения \n7) ' \
        'После поражения цель обязана без сопротивления отойти с тобой в сторонку и передать свой активный заказ, ' \
        'ID своей жертвы, а также выданный ей неиспользованный браслет.\n\n' \
        '❗Ограничения игры❗\n1) Насилие запрещено\n2) Устранять разрешено только используя спец.набор, выданный ' \
        'организаторами\nВ спец. набор входят слэп-браслеты, обезвреживающие клонов. Для устранения клона ' \
        'необходимо захлопнуть браслет на руке или ноге клона.\n3) Любой клон (кроме жертвы) может прервать ' \
        'устранение, сказав «Ты ненастоящий», если человек выполняющий устранение держит в руках браслет\n' \
        '4) Устранять можно на 1,2,5,6,7 этажах 2-го учебного корпуса. В лифтах устранять можно. На лестницах ' \
        'устранять нельзя по соображениям безопасности.\n5) Устраниние запрещено, если хотя бы один из игроков ' \
        '(клон или охотящийся на него участник) находится на занятии (перерывы между ' \
        'парами и между половинами пары не являются занятиями)'

