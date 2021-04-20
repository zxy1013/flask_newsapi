from flask import Flask
from apps.apis.news_api import *
from apps.apis.user_api import *
from exts import db, cors, cache
from settings import DevelopmentConfig

# 对CACHE的配置 redis需要先启动 D:\wendang\redis>redis-server
config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': '127.0.0.1',
    'CACHE_REDIS_PORT': 6379
}

def create_app():
    app = Flask(__name__, static_folder='../static')
    app.config.from_object(DevelopmentConfig)
    db.init_app(app=app)
    # app关联跨域
    cors.init_app(app=app, supports_credentials=True)
    # 缓存导入
    cache.init_app(app=app, config=config)
    # 注册蓝图
    app.register_blueprint(news_bp)
    app.register_blueprint(user_bp)
    print(app.url_map)
    return app
