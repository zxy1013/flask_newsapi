from flask import Blueprint, g
from flask_restful import Api, Resource, fields, marshal_with, reqparse, marshal
from apps.models.news_model import *
from apps.util import login_required
from exts import db
news_bp = Blueprint('news', __name__)
# 绑定api和蓝图
api = Api(news_bp)



# get type输出格式
types_fields = {
    'id': fields.Integer,
    'name': fields.String(attribute='type_name')
}

# post的传入
type_parser = reqparse.RequestParser()
type_parser.add_argument('typeName', type=str, required=True, help='必须添加新闻分类名字', location='form')

# patch修改的传入
update_type_parser = type_parser.copy()
update_type_parser.add_argument('id', type=int, required=True, help='必须添加要修改的分类id')

# delete删除的传入
delete_type_parser = reqparse.RequestParser()
delete_type_parser.add_argument('id', type=int, required=True, help='必须添加要删除的分类id')

# 新闻类型api '/types'
class NewsTypeApi(Resource):
    @marshal_with(types_fields) # 按types_fields的格式输出
    def get(self):
        types = NewsType.query.all()
        return types  # NewsType属于自定义的类型

    # 使用post添加新闻类型
    def post(self):
        args = type_parser.parse_args()
        typeName = args.get('typeName')
        # 数据库添加
        newsType = NewsType()
        newsType.type_name = typeName
        db.session.add(newsType)
        db.session.commit()
        return marshal(newsType, types_fields)  # NewsType类型输出

    # patch修改分类名称
    def patch(self):
        # 获取传入的值
        args = update_type_parser.parse_args()
        # 获取id和type
        typeId = args.get('id')
        new_type_name = args.get('typeName')
        # 修改
        type_obj = NewsType.query.get(typeId)
        if type_obj:
            type_obj.type_name = new_type_name
            db.session.commit()
            data = {
                'status': 200,
                'msg': '修改成功',
                'type': marshal(type_obj, types_fields)
            }
        else:
            data = {
                'status': 400,
                'msg': '类型查找失败！'
            }
        return data

    # 删除分类名称
    def delete(self):
        args = delete_type_parser.parse_args()
        typeId = args.get('id')
        type_obj = NewsType.query.get(typeId)
        if type_obj:
            db.session.delete(type_obj)
            db.session.commit()
            data = {
                'status': 200,
                'msg': '类型删除成功'
            }
        else:
            data = {
                'status': 400,
                'msg': '类型查找失败'
            }
        return data






# NewsListApi get的传入
news_parser = reqparse.RequestParser()
news_parser.add_argument('typeid', type=int, help='必须添加新闻类型id', required=True)
news_parser.add_argument('page', type=int)
# 想要输出的格式
'''
{
  'has_more':true,
  'data':[],
  'return_count':8,
  'html':null,
}
'''

# 对authorname的自定义fields类型
class AuthorName(fields.Raw):
    def format(self, value):
        return value.username

# NewsListApi 新闻列表输出中每条新闻的格式
news_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'desc': fields.String,
    'datetime': fields.DateTime(attribute='date_time'),
    'author': AuthorName(attribute='author'), # news.author.username
    'url': fields.Url('news.newsdetail', absolute=True) # 构建uri 拼接id http://127.0.0.1:5000/newsdetail/1
}

# 新闻列表的api
class NewsListApi(Resource):
    # 获取某个新闻分类下的新闻
    def get(self):
        args = news_parser.parse_args()
        typeid = args.get('typeid')
        # 分页
        page = args.get('page', 1)
        pagination = News.query.filter(News.news_type_id == typeid).paginate(page=page, per_page=8)
        data = {
            'has_more': pagination.has_next,
            'data': marshal(pagination.items, news_fields),  # [news,news,news,....]
            'return_count': len(pagination.items),
            'html': 'null',
        }
        return data






# NewsDetailApi get 回复的格式
reply_fields = {
    'user': AuthorName(attribute='user'),
    'content': fields.String,
    'datetime': fields.DateTime(attribute='date_time'),
    'lovenumber': fields.Integer(attribute='love_num')
}

# NewsDetailApi get 评价的格式
comment_fields = {
    'user': AuthorName(attribute='user'),
    'content': fields.String,
    'datetime': fields.DateTime(attribute='date_time'),
    'lovenumber': fields.Integer(attribute='love_num'),
    'replys': fields.List(fields.Nested(reply_fields))
}

# NewsDetailApi get 返回的套叠结构
news_detail_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'datatime': fields.DateTime(attribute='date_time'),
    'author': AuthorName(attribute='author'),
    'comments': fields.List(fields.Nested(comment_fields)) # 套叠
}

class NewsDetailApi(Resource):
    @marshal_with(news_detail_fields)
    def get(self, id):
        news = News.query.get(id)
        return news






# 定义NewsApi添加的传入
add_news_parser = reqparse.RequestParser()
add_news_parser.add_argument('title', type=str, required=True, help='必须填写新闻标题')
add_news_parser.add_argument('content', type=str, required=True, help='必须填写新闻主体内容')
add_news_parser.add_argument('typeid', type=int, required=True, help='必须填写新闻类型id')

class NewsApi(Resource):
    @login_required # 设置登录装饰器 func=post
    def post(self):
        args = add_news_parser.parse_args()
        title = args.get('title')
        content = args.get('content')
        typeid = args.get('typeid')
        # 数据库添加
        news = News()
        news.title = title
        news.content = content
        news.desc = content[:100] + '.....'
        news.news_type_id = typeid
        news.user_id = g.user.id
        db.session.add(news)
        db.session.commit()
        data = {
            'status': 200,
            'msg': '新闻发布成功！',
            'news': marshal(news, news_detail_fields)
        }
        return data

    @login_required
    def patch(self):
        return {'msg': '新闻修改成功！'}





# 添加api及路径
api.add_resource(NewsTypeApi, '/types')
api.add_resource(NewsListApi, '/newslist')
api.add_resource(NewsDetailApi, '/newsdetail/<int:id>', endpoint='newsdetail')
api.add_resource(NewsApi, '/news')





# get http://127.0.0.1:5000/types 展示分类名称
# post http://127.0.0.1:5000/types body-x-www中设置typeName= 添加分类名称
# patch http://127.0.0.1:5000/types body-x-www中设置id= typeName= 修改分类名称
# delete http://127.0.0.1:5000/types body-x-www中设置id= 删除分类名称
# get http://127.0.0.1:5000/newslist params中设置typeid=1 展示newslist
# get 点击显示的url 点发送 可显示http://127.0.0.1:5000/newsdetail/1 中的内容
# post http://127.0.0.1:5000/news headers中设置Authorization=token body中设置title content typeid
# token 9a3036ec75234326ad55ee169d2b242d302
# patch http://127.0.0.1:5000/news headers中设置Authorization=token