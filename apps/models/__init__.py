from datetime import datetime
from exts import db

# 定义父类 让所有的数据库表继承
class BaseModel(db.Model):
    __abstract__ = True # 表明其为抽象类 不单独做为模型出现 只被继承使用
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_time = db.Column(db.DateTime, default=datetime.now)