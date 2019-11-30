from telebot import apihelper
from peewee import DoesNotExist
from functools import wraps
import logging

import telebot
import config
from mwt import *
from config import db
from users import User, Role

import random
import string


def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

logger = logging.getLogger('bot')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(token=config.token)
'''
# using proxy in Russia
apihelper.proxy = {
    # 'http': 'http://46.101.149.132:3128',
    # 'https': 'https://46.101.149.132:3128'
    # 'http': 'http://79.138.99.254:8080',
    # 'https': 'https://79.138.99.254:8080'
     'http': 'http://5.148.128.44:80',
     'https': 'https://5.148.128.44:80'
    # 'http': 'http://167.99.242.198:8080',
    # 'https': 'https://167.99.242.198:8080'
}
'''
# create tables in db
db.connect()
db.create_tables([User])

# create GOD if not exists
try:
    god = User.get(User.tg_id == config.creatorID)
except DoesNotExist:
    god = User.create(tg_id=config.creatorID, username=config.creatorUsername, name='Yury', role=Role.GOD)


@MWT(timeout=5*60)
def get_privilege_ids(role):
    logger.info("Update list of %s", role)
    return [user.tg_id for user in User.select().where(User.role >= role)]


def restricted(role):

    def wrapper(func):
        @wraps(func)
        def wrapped(message, *args, **kwargs):
            user_id = message.chat.id
            if user_id not in get_privilege_ids(role):
                logger.warning("Unauthorized access to <{}> by {}.".format(func.__name__, message.from_user.username))
                return
            return func(message, *args, **kwargs)
        return wrapped

    return wrapper


def guard():

    def wrapper(func):
        @wraps(func)
        def wrapped(message, *args, **kwargs):
            if message.chat.id in config.ban_list:
                logger.warning("Banned user @{}.".format(message.from_user.username))
                return
            return func(message, *args, **kwargs)
        return wrapped

    return wrapper


def check_text(message, func):
    if message.text is None:
        logger.warning("Wrong data format in <{}> by {}".format(func.__name__, message.from_user.username))
        bot.send_message(message.chat.id, config.warningWrongDataFormat)
        return False
    return True


def check_group_number(n):
    return 100 < n < 700 and n % 100 < 50


@bot.message_handler(commands=['start'])
@guard()
def start_cmd(message):
    bot.send_message(message.chat.id, config.welcomeMsg)
    bot.register_next_step_handler(message, get_surname)


@bot.message_handler(commands=['reg'])
@guard()
def reg_cmd(message):
    bot.send_message(message.chat.id, config.getSurname)
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    if not check_text(message, get_surname):
        bot.send_message(message.chat.id, config.regAgain)
        return
    bot.send_message(message.chat.id, config.getName)
    bot.register_next_step_handler(message, get_name, message.text)


def get_name(message, surname='NONE'):
    if not check_text(message, get_name):
        bot.send_message(message.chat.id, config.regAgain)
        return
    bot.send_message(message.chat.id, config.getGroup)
    bot.register_next_step_handler(message, get_group, surname, message.text)


def get_group(message, surname='NONE', name='NONE'):
    if not check_text(message, get_group):
        bot.send_message(message.chat.id, config.regAgain)
        return
    n = message.text
    if not n.isdecimal() or not check_group_number(int(n)):
        bot.send_message(message.chat.id, config.warningWrongGroup)
        return
    n = int(n)
    bot.send_message(message.chat.id, config.getAvatar)
    bot.register_next_step_handler(message, get_avatar, surname, name, n)


def get_avatar(message, surname='NONE', name='NONE', group=0):
    if message.photo is None:
        bot.send_message(message.chat.id, config.regAgain)
        return
    photo_id = message.photo[0].file_id
    try:
        user = User.get(User.tg_id == message.chat.id)
        if user.role == Role.NONE:
            bot.send_message(user.tg_id, config.alreadyKilled)
            logger.warning('Trying to re-register: @{}'.format(user.username))
            return
        user.surname = surname
        user.name = name
        user.group = group
        user.avatar = photo_id
        user.save()
    except DoesNotExist:
        user = User.create(tg_id=message.chat.id, surname=surname, name=name, group=group, role=Role.PLAYER,
                           username=message.from_user.username, avatar=photo_id)
    logger.info('New user {} {} group {} - @{} was registered'.format(user.surname, user.name,
                                                                      user.group, user.username))
    bot.send_message(config.creatorID, 'New user @{}'.format(user.username), disable_notification=True)
    bot.send_photo(config.creatorID, user.avatar, disable_notification=True)
    bot.send_message(message.chat.id, config.successfulReg)


@bot.message_handler(commands=['help'])
@guard()
def help_cmp(message):
    bot.send_message(message.chat.id, config.helpMsg)


@bot.message_handler(commands=['prof'])
def prof_cmd(message):
    try:
        user = User.get(User.tg_id == message.chat.id)
    except DoesNotExist:
        logger.error('No such user in command prof!')
        bot.send_message(message.chat.id, config.warningSomethingWentWrong)
        return
    user.profhome = True
    user.save()
    bot.send_message(message.chat.id, 'Success!')
    logger.info('New PROFHOME @{}'.format(user.username))


@bot.message_handler(commands=['begin'])
@restricted(Role.GOD)
def begin_cmd(message):
    logger.info('GAME STARTED - @{}'.format(message.from_user.username))
    shuffle()
    cnt_err = 0
    for user in User.select().where(User.role == Role.PLAYER):
        bot.send_message(user.tg_id, config.startGame)
        try:
            target = User.get(User.tg_id == user.target_id)
            next_target(user, target)
        except DoesNotExist:
            cnt_err += 1
            bot.send_message(user.tg_id, 'Что-то не получилось в распределении игроков, пожалуйста, '
                                         'обратитесь к организаторам')
    bot.send_message(message.chat.id, 'Success!' if cnt_err == 0 else 'Something went wrong')


def set_target(user, target):
    user.target_id = target.tg_id
    user.target_key = random_string()
    user.save()


def shuffle():
    users = []
    prof = []
    for user in User.select().where(User.role == Role.PLAYER):
        if user.profhome:
            prof.append(user)
        else:
            users.append(user)
    random.shuffle(users)
    random.shuffle(prof)
    delta = len(users) - len(prof)
    if delta < 0:
        users, prof = prof, users
        delta = -delta

    delta = max(len(users) // delta, 1) if delta > 0 else 1
    cycle = []
    cur_user = 0
    for u in prof:
        for i in range(delta):
            user = users[cur_user + i]
            if len(cycle):
                set_target(cycle[-1], target=user)
            cycle.append(user)
        cur_user += delta
        set_target(cycle[-1], target=u)
        cycle.append(u)
    for i in range(cur_user, len(users)):
        set_target(cycle[-1], target=users[i])
        cycle.append(users[i])
    set_target(cycle[-1], target=cycle[0])


@bot.message_handler(commands=['reset'])
@restricted(Role.GOD)
def reset_cmd(message):
    for user in User.select().where(User.role <= Role.PLAYER):
        user.target_id = 0
        user.target_key = ''
        user.score = 0
        user.role = Role.PLAYER
        user.save()
    bot.send_message(message.chat.id, 'Success!')


@bot.message_handler(commands=['kill'])
@restricted(Role.PLAYER)
def kill_cmd(message):
    bot.send_message(message.chat.id, config.getTargetID)
    bot.register_next_step_handler(message, kill_target)


def kill_target(message):
    check_text(message, kill_target)
    if len(User.select().where(User.role == Role.PLAYER)) == 1:
        bot.send_message(message.chat.id, config.alreadyWon)
        return
    try:
        user = User.get(User.tg_id == message.chat.id)
        target = User.get(User.tg_id == user.target_id)
    except DoesNotExist:
        bot.send_message(message.chat.id, config.errorUnexpected)
        return

    if message.text == target.target_key:
        logger.info('User {} {} group {} committed a murder!'.format(user.surname, user.name, user.group))
        user.target_key = target.target_key
        user.target_id = target.target_id
        user.score += 1
        user.save()
        kill(target)
        if len(User.select().where(User.role == Role.PLAYER)) == 1:
            bot.send_message(user.tg_id, config.congrats)
            bot.send_message(config.creatorID, 'Победитель - {} {} группа {}'.format(user.surname, user.name,
                                                                                     user.group))
            bot.send_photo(config.creatorID, user.avatar)
            logger.info('WINNER {} {} группа {}'.format(user.surname, user.name, user.group))
            return

        bot.send_message(message.chat.id, config.successfulKill)
        try:
            target = User.get(User.tg_id == user.target_id)
        except DoesNotExist:
            bot.send_message(message.chat.id, 'Ошибка в назначении жертвы :( Обратись к организаторам')
        next_target(user, target)
    else:
        bot.send_message(message.chat.id, config.errorWrongTargetID)
        logger.info('Wrong targetID from @{}\nGot {} expected {}'.format(message.from_user.username,
                                                                         message.text, target.target_key))


def next_target(user, target):
    bot.send_message(user.tg_id, config.newTarget.format(target.surname, target.name, target.group,
                                                         user.target_key))
    bot.send_photo(user.tg_id, target.avatar)


def kill(user):
    bot.send_message(user.tg_id, config.killed.format(user.score))
    user.role = Role.NONE
    user.target_id = 0
    user.target_key = ''
    user.save()
    logger.info('User {} {} group {} was killed! Victims: {}'.format(user.surname, user.name, user.group, user.score))


@bot.message_handler(commands=['show'])
@restricted(Role.PLAYER)
def show_cmd(message):
    try:
        user = User.get(User.tg_id == message.chat.id)
        target = User.get(User.tg_id == user.target_id)
    except DoesNotExist:
        bot.send_message(message.chat.id, config.error)
        return
    next_target(user, target)


@bot.message_handler(commands=['force_kill'])
@restricted(Role.ADMIN)
def force_kill_cmd(message):
    l = message.text.split(' ', maxsplit=1)
    if len(l) < 2:
        bot.send_message(message.chat.id, 'Wrong format!\n/force_kill username')
        return
    username = l[1]
    try:
        user = User.get(User.username == username)
        prev = User.get(User.target_id == user.tg_id)
        target = User.get(User.tg_id == user.target_id)
    except DoesNotExist:
        bot.send_message(message.chat.id, 'User not found!')
        return
    prev.target_id = user.target_id
    prev.target_key = user.target_key
    bot.send_message(prev.tg_id, config.forceKill)
    next_target(prev, target)
    prev.save()
    kill(user)
    bot.send_message(message.chat.id, 'Success!')


@bot.message_handler(commands=['show_cycle'])
@restricted(Role.ADMIN)
def cycle_cmd(message):
    spacer = '| \nV'
    try:
        user = User.get(User.role == Role.PLAYER)
        start_tg_id = user.tg_id
        msg = '{} {} группа {} @{} (Число жертв: {})\n'.format(user.surname, user.name,user.group,
                                                               user.username, user.score) + spacer + '\n'
        cur_tg_id = user.target_id
        while cur_tg_id != start_tg_id:
            user = User.get(User.tg_id == cur_tg_id)
            msg += '{} {} группа {} @{} (Число жертв: {})\n'.format(user.surname, user.name, user.group,
                                                                    user.username, user.score) + spacer + '\n'
            cur_tg_id = user.target_id
    except DoesNotExist:
        bot.send_message(message.chat.id, 'Ошибка!')
        return
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['everyone'])
@restricted(Role.ADMIN)
def everyone_cmd(message):
    l = message.text.split(' ', maxsplit=1)
    if len(l) < 2:
        bot.send_message(message.chat.id, 'Wrong format!\n/everyone <message>')
        return
    everyone(l[1])

    bot.send_message(message.chat.id, 'Success!')


def everyone(msg):
    for user in User.select():
        bot.send_message(user.tg_id, msg)


@bot.message_handler(commands=['wall'])
@restricted(Role.ADMIN)
def wall_cmd(message):
    l = message.text.split(' ', maxsplit=1)
    if len(l) < 2:
        bot.send_message(message.chat.id, 'Wrong format!\n/wall <message>')
        return
    message.text = l[1]

    for user in User.select().where(User.role > Role.PLAYER):
        bot.send_message(user.tg_id, message.text)
    bot.send_message(message.chat.id, 'Success!')


@bot.message_handler(commands=['make_god'])
@restricted(Role.GOD)
def make_god_cmd(message):
    l = message.text.split(' ', maxsplit=1)
    if len(l) < 2:
        bot.send_message(message.chat.id, 'Wrong format!\n/make_god username')
        return
    username = l[1]
    try:
        user = User.get(User.username == username)
    except DoesNotExist:
        bot.send_message(message.chat.id, 'No such user!')
        return
    user.role = Role.GOD
    user.save()
    logger.info('User {} - {} become a God'.format(user.name, user.username))
    bot.send_message(message.chat.id, 'Success!')
    bot.send_message(user.tg_id, 'You become a God!')


@bot.message_handler(commands=['make_admin'])
@restricted(Role.GOD)
def make_admin_cmd(message):
    l = message.text.split(' ', maxsplit=1)
    if len(l) < 2:
        bot.send_message(message.chat.id, 'Wrong format!\n/make_admin username')
        return
    username = l[1]
    try:
        user = User.get(User.username == username)
    except DoesNotExist:
        bot.send_message(message.chat.id, 'No such user!')
        return
    if user.tg_id == config.creatorID:
        bot.send_message(message.chat.id, "This is my creator! I can't do that")
        return
    user.role = Role.ADMIN
    user.save()
    logger.info('User {} - {} become an admin'.format(user.name, user.username))
    bot.send_message(message.chat.id, 'Success!')
    bot.send_message(user.tg_id, 'You become an Admin!')


@bot.message_handler(commands=['update_photo'])
@restricted(Role.PLAYER)
def update_photo_cmd(message):
    bot.send_message(message.chat.id, config.getAvatar)
    bot.register_next_step_handler(message, get_photo)


def get_photo(message):
    if message.photo is None:
        bot.send_message(message.chat.id, 'Попробуйте еще раз')
        return
    photo_id = message.photo[0].file_id
    try:
        user = User.get(User.tg_id == message.chat.id)
        user.avatar = photo_id
        user.save()
        bot.send_message(message.chat.id, 'Успешно!')
        bot.send_message(config.creatorID, 'User {} {} group {} @{} updated photo'.format(user.surname, user.name,
                                                                                          user.group, user.username))
        bot.send_photo(config.creatorID, photo_id, disable_notification=True)
    except DoesNotExist:
        bot.send_message(message.chat.id, 'Ошибка!')
        return


@bot.message_handler(commands=['get_photo'])
@restricted(Role.ADMIN)
def get_photo_cmd(message):
    l = message.text.split(' ', maxsplit=1)
    if len(l) < 2:
        bot.send_message(message.chat.id, 'Wrong format!\n/get_photo username')
        return
    username = l[1]
    try:
        user = User.get(User.username == username)
    except DoesNotExist:
        bot.send_message(message.chat.id, 'No such user!')
        return
    bot.send_photo(message.chat.id, user.avatar)


@bot.message_handler(commands=['ban'])
@restricted(Role.GOD)
def ban_cmd(message):
    l = message.text.split(' ', maxsplit=1)
    if len(l) < 2:
        bot.send_message(message.chat.id, 'Wrong format!\n/ban tg_id')
        return
    tg_id = l[1]
    if not tg_id.isdecimal():
        bot.send_message(message.chat.id, 'tg_id must be integer!')
        return
    config.ban_list.append(int(tg_id))


@bot.message_handler(content_types=['sticker'])
@guard()
def echo_sticker(message):
    bot.send_message(message.chat.id, 'Классный стикер!')


@bot.message_handler(content_types=['text'])
@guard()
def echo_text(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)
