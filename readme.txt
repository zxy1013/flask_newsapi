跨域问题来源于JavaScript的"同源策略"，即只有协议+主机名+端口号 (如存在)相同,才允许相互访问。
也就是说JavaScript只能访问和操作自己域下的资源，不能访问和操作其他域下的资源。
跨域问题是针对JS和ajax的，html本身没有跨域问题。

后端解决跨域问题
pip install flask-cors
使用第三方扩展 exts中创建
from flask_cors import CORS
cors= CORS()
与app进行绑定即可
cors.init_app(app=app,supports_credentials=True)


蓝图与api配合使用
user_bp = Blueprint('user', __name__)
蓝图绑定api 蓝图注册到app上
api = Api(user_bp)
app.register_blueprint(user_bp)
# 定义api
class xxxxApi(Resource):
    pass
# 绑定路由
api.add_resource(xxxxApi,'/xxxx')


在OAuth协议中，token是在输入了用户名和密码之后获取的，利用这个token可以拥有查看或者操作相应的资源的权限。
有这些权限，是因为服务器知道你是谁以后赋予你的，所以token，其实就是你的一个“代表”，或者说完全能代表你的“通行证”。