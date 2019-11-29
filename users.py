from peewee import *
from enum import IntEnum
from config import db


class Role(IntEnum):
    NONE = 0
    PLAYER = 1
    ADMIN = 2
    GOD = 3


class RoleField(Field):
    field_type = 'smallint'

    def db_value(self, value):
        return int(value)

    def python_value(self, value):
        return Role(value)


class User(Model):
    tg_id = IntegerField(unique=True)
    surname = CharField(null=True)
    name = CharField(null=True)
    group = IntegerField(null=True)
    username = CharField(null=True)
    role = RoleField(default=Role.NONE)
    avatar = CharField(null=True)
    target_id = IntegerField(default=0)
    target_key = CharField(null=True)
    profhome = BooleanField(default=False)
    score = IntegerField(default=0)

    class Meta:
        database = db
