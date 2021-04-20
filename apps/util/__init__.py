# 发送短信息
import random
from flask import request, g, jsonify
from flask_restful import abort
from apps.models.user_model import *
from apps.util import smssend
from exts import cache

def sendmess(mobile):
    r = str(int(random.random( ) * 10000 // 1))
    text = "您的验证码是：%s。请不要把验证码泄露给其他人。" % r
    ret = smssend.send_sms(text, mobile)
    ret = eval(ret.decode('utf-8'))
    # print(ret)
    if ret is not None:
        if ret[ "code" ] == 2:
            # 使用缓存 过期时间为180s
            cache.set(mobile, str(r), timeout=18000)
            return jsonify(code=2, msg='短信发送成功')
        else:
            # cache.set(mobile, str(r), timeout=18000)
            return jsonify(code=0, msg='短信未发送成功')

def check_user():
    auth = request.headers.get('Authorization')
    if not auth:
        # 抛出异常 Raise a HTTPException for the given http_status_code.
        abort(401, msg='请先登录')
    mobile = cache.get(auth)
    if not mobile:
        abort(401, msg='无效令牌')
    user = User.query.filter(User.phone == mobile).first()
    if not user:
        abort(401, msg='此用户已被管理员删除')
    g.user = user


def login_required(func):
    def wrapper(*args, **kwargs):
        check_user()
        return func(*args, **kwargs)
    return wrapper