from apps.models import BaseModel
from exts import db

class NewsType(BaseModel):
    # 数据库表名
    __tablename__ = 'news_type'
    type_name = db.Column(db.String(50), nullable=False)
    # newstype取news
    '''
    types = NewsType.query.all()
    for i in types:
        print(i.newslist) # [<News 1>, <News 2>]
    '''
    # news访问newstype
    '''
    news = News.query.first()
    print(news.newstype.type_name) # 热点'''
    # 一对多的一构建relationship 多的构建外键
    newslist = db.relationship('News', backref='newstype')

class News(BaseModel):
    __tablename__ = 'news'
    title = db.Column(db.String(100), nullable=False)
    # 新闻概要
    desc = db.Column(db.String(255))
    # db.Text 文本类型
    content = db.Column(db.Text, nullable=False)
    news_type_id = db.Column(db.Integer, db.ForeignKey('news_type.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='news')
    def __str__(self):
        return self.title

class Comment(BaseModel):
    __tablename__ = 'comment'
    content = db.Column(db.String(255), nullable=False)
    love_num = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    replys = db.relationship('Reply', backref='comment')
    def __str__(self):
        return self.content

class Reply(BaseModel):
    __tablename__ = 'reply'
    content = db.Column(db.String(255), nullable=False)
    love_num = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    def __str__(self):
        return self.content