import uuid
import random
from flask import Blueprint, session
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal
from werkzeug.security import generate_password_hash, check_password_hash
from apps.models.user_model import User
from apps.util import sendmess
from exts import cache, db

user_bp = Blueprint('user', __name__)
api = Api(user_bp)

# 定义传入
sms_parser = reqparse.RequestParser()
sms_parser.add_argument('mobile', type=inputs.regex(r'^1[356789]\d{9}$'), help='手机号码格式错误', required=True,
                        location=['form', 'args'])
# 发送手机验证码类api
class SendMessageApi(Resource):
    def post(self):
        args = sms_parser.parse_args()
        mobile = args.get('mobile')
        return sendmess(mobile)


# 输入拷贝sms_parser中的对象
lr_parser = sms_parser.copy()
lr_parser.add_argument('code', type=inputs.regex(r'^\d{0,4}$'), help='必须输入四位数字验证码', required=True, location='form')

# 自定义输出
user_fields = {
    'id': fields.Integer,
    'username': fields.String
}

# 用户的登录和注册api
class LoginAndRegisterApi(Resource):
    def post(self):
        args = lr_parser.parse_args()
        mobile = args.get('mobile')
        code = args.get('code')
        cache_code = cache.get(mobile)
        if cache_code and code == cache_code:
        # if code == '1234':
            # 数据库中查找是否存在此mobile用户
            user = User.query.filter(User.phone == mobile).first()
            if not user: # 无用户
                # 注册处理
                user = User()
                user.phone = mobile
                s = ''
                for i in range(10):
                    ran = random.randint(0, 9)
                    s += str(ran)
                user.username = '用户' + s
                db.session.add(user)
                db.session.commit()
            # 登录处理 记录登录状态：session(一个用户一个session)，cookie，cache(redis所有用户用一个大池子)，token
            token = str(uuid.uuid4()).replace('-', '') + str(random.randint(100, 999))
            # print('token:', token)
            # 存储用户的登录信息
            cache.set(token, mobile)
            return marshal(user,user_fields) # 用装饰器则上下需返回一样格式的内容
            # return {'status': 200, 'msg': '用户登录成功', 'token': token}
        else:
            return {'errmsg': '验证码错误', 'status': 400}


# 忘记密码api
class ForgetPasswordApi(Resource):
    def get(self):
        s = 'QWERTYUIOPLKJHGFDSAZXCVBNMzxcvbnmlkjhgfdsaqwertyuiop1234567890'
        code = '' # 产生code让前端产生
        for i in range(4):
            ran = random.choice(s)
            code += ran
        # 保存code 用session 因为一个用户一个session 避免找不到合适的key从而覆盖值
        session['code'] = code
        return {'code': code}


# 申请重置密码的输入
reset_parser = sms_parser.copy()
reset_parser.add_argument('imageCode', type=inputs.regex(r'^[a-zA-Z0-9]{4}$'), help='必须输入正确格式的验证码')

# 定义重置密码api
class ResetPasswordApi(Resource):
    def get(self):
        args = reset_parser.parse_args()
        mobile = args.get('mobile')
        imageCode = args.get('imageCode')
        code = session.get('code') # 取出忘记密码设置的图片字符串
        if code and imageCode.lower() == code.lower():
            # 判断手机号码
            user = User.query.filter(User.phone == mobile).first()
            if user:
                return sendmess(mobile)
            else:
                return {'status': 400, 'msg': '此用户未注册，请注册'}
        else:
            return {'status': 400, 'msg': '验证码输入有误或者超时'}


# 更新密码时客户端要传入的信息
# 正则表达式有在线测试的网站
update_parser = lr_parser.copy()
update_parser.add_argument('password'
                           , type=inputs.regex(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[a-zA-Z0-9]{8,10}$')
                           , help='必须包含大小写字母和数字的组合，不能使用特殊字符'
                           , location='form')
update_parser.add_argument('repassword'
                           , type=inputs.regex(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[a-zA-Z0-9]{8,10}$')
                           , help='必须包含大小写字母和数字的组合，不能使用特殊字符'
                           , location='form')

# 登录时需要前端传入的内容
password_login_parser = sms_parser.copy()
password_login_parser.add_argument('password', type=str, help='必须输入密码', required=True, location='form')

# 手机号加密码登录和修改密码api
class UserApi(Resource):
    def post(self):
        args = password_login_parser.parse_args()
        mobile = args.get('mobile')
        password = args.get('password')
        # 判断用户
        user = User.query.filter(User.phone == mobile).first()
        if user:
            if check_password_hash(user.password, password):
                # 说明用户登录成功
                token = str(uuid.uuid4()).replace('-', '') + str(random.randint(100, 999))
                # print(token)
                # 存储用户的登录信息
                cache.set(token, mobile)
                return {'status': 200, 'msg': '用户登录成功', 'token': token}
        return {'status': 400, 'msg': '账户名或者密码有误！'}

    def put(self):
        args = update_parser.parse_args()
        code = args.get('code')
        mobile = args.get('mobile')
        cache_code = cache.get(mobile)

        # 判断验证码是否输入正确
        if cache_code and cache_code == code:
            user = User.query.filter(User.phone == mobile).first()
            password = args.get('password')
            repassword = args.get('repassword')
            # 判断密码是否输入一致
            if password == repassword:
                user.password = generate_password_hash(password)
                db.session.commit()
                return {'status': 200, 'msg': '设置密码成功'}
            else:
                return {'status': 400, 'msg': '两次密码不一致'}
        else:
            return {'status': 400, 'msg': '验证码有误'}

# 发送手机验证码
api.add_resource(SendMessageApi, '/sms')
# 验证码登录
api.add_resource(LoginAndRegisterApi, '/codelogin')
# 忘记密码
api.add_resource(ForgetPasswordApi, '/forget')
# 重置密码
api.add_resource(ResetPasswordApi, '/reset')
# 手机号密码登录以及更新密码
api.add_resource(UserApi, '/user')


# 先 post http://127.0.0.1:5000/sms 设置moblie # 635 发送验证码
# post http://127.0.0.1:5000/codelogin 设置moblie  code=635 手机号码登录
# get http://127.0.0.1:5000/forget # LCSE 忘记密码
# get http://127.0.0.1:5000/reset 设置mobile imageCode=LCSE  # 863 重置密码请求
# put http://127.0.0.1:5000/user 设置mobile password repassword=zXy16111 重置密码
# post http://127.0.0.1:5000/user 设置mobile password=zXy16111 手机密码登录 记录令牌9a3036ec75234326ad55ee169d2b242d302