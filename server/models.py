from tortoise import models, fields


# 用户
class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    is_admin = fields.BooleanField()
    token = fields.CharField(max_length=255, null=True)


# 应用
class App(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    token = fields.CharField(max_length=255)


# 账户
class Account(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    account = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    token = fields.CharField(max_length=255, null=True)
    apps = fields.CharField(max_length=1000, null=True)


# 字典
class Dict(models.Model):
    id = fields.IntField(pk=True)
    key = fields.CharField(max_length=255)
    value = fields.CharField(max_length=5000)


# 历史数据
class History(models.Model):
    id = fields.IntField(pk=True)
    account = fields.ForeignKeyField("models.Account", related_name="history")
    app = fields.ForeignKeyField("models.App", related_name="history")
    question = fields.CharField(max_length=50000)
    answer = fields.CharField(max_length=50000)
    question_audio_url = fields.CharField(max_length=5000, null=True)
    answer_audio_url = fields.CharField(max_length=5000, null=True)
    question_time = fields.DatetimeField(null=True)
    answer_time = fields.DatetimeField(null=True)
