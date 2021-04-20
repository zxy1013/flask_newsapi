# -*-coding:utf-8-*-
# @ Auth:zhao xy
# @ Time:2021/3/24 14:46
# @ File:message_send.py

import httplib2
import urllib

host = "106.ihuyi.com"
sms_send_uri = "/webservice/sms.php?method=Submit"

# 查看用户名 登录用户中心->验证码通知短信>产品总览->API接口信息->APIID
account = "C38332865"
# 查看密码 登录用户中心->验证码通知短信>产品总览->API接口信息->APIKEY
password = "0633314e17dc3dc293a25cb38ff2cea1"


def send_sms(text, mobile):
	params = urllib.parse.urlencode(
		{'account': account, 'password': password, 'content': text, 'mobile': mobile, 'format': 'json'})
	headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
	conn = httplib2.HTTPConnectionWithTimeout(host, port=80, timeout=30)
	conn.request("POST", sms_send_uri, params, headers)
	response = conn.getresponse( )
	response_str = response.read( )
	conn.close( )
	return response_str

if __name__ == '__main__':
	mobile = "17629075993"
	text = "您的验证码是：121254。请不要把验证码泄露给其他人。"
	print(send_sms(text, mobile)) # 返回 b'{"code":2,"msg":"\xe6\x8f\x90\xe4\xba\xa4\xe6\x88\x90\xe5\x8a\x9f","smsid":"16165686731585006595"}'