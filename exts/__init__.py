from flask_caching import Cache
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# 创建跨域支持
cors = CORS()
cache = Cache()