import re

from flask import Blueprint, jsonify, request, make_response
from exts import *
from werkzeug.security import check_password_hash, generate_password_hash
from .decorators import jwt_encode, jwt_required, current_identity
from models import UserModel
from blueprint import RETCODE
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
from .utils import gen_response_data
from .decorators import register_required
import random

bp = Blueprint('user', __name__, url_prefix="/api/user")


@bp.route('/valid_code', methods=['POST'])
def valid_code():
    # 获取数据
    phone = request.json.get('phone')
    try:
        # 生成四位随机数字字母作为验证码
        code = random.sample('0123456789', 4)
        code = "".join(code)
        # 将验证码保存到redis中，第一个参数是key，第二个参数是value，第三个参数表示60秒后过期
        redis_store.set('valid_code:{}'.format(phone), code, 60)
        sms_request = SendSmsRequest()
        sms_request.set_accept_format('json')
        sms_request.set_SignName("阿里云短信测试")
        sms_request.set_TemplateCode("SMS_154950909")
        sms_request.set_PhoneNumbers(phone)
        sms_request.set_TemplateParam("{\"code\":\"%s\"}" % code)
        sms_response = client.do_action_with_exception(sms_request)
        # 这里用输出验证码来代替短信发送验证码
        return sms_response
    except Exception as e:
        print(e)
        return jsonify(status='失败', msg="验证码发送失败")


@bp.route("/register", methods=['POST'])
@register_required
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    confirm_password = request.json.get('confirm_password', None)
    phone = request.json.get('phone', None)
    r_code = request.json.get('code', None)
    code = redis_store.get('valid_code:{}'.format(phone))
    if code is None:
        response_data = gen_response_data(RETCODE.CODEEXPIRES, '验证码过期')
        return jsonify(response_data)
    if code != r_code:
        response_data = gen_response_data(RETCODE.CODEERR, '验证码错误')
        return jsonify(response_data)
    if password != confirm_password:
        response_data = gen_response_data(RETCODE.PWDDIFF, '两次密码不一致')
        return jsonify(response_data)
    try:
        user = UserModel(username=username, password=generate_password_hash(password), phone=phone, icon='')
        db.session.add(user)
        db.session.commit()
        response_data = gen_response_data(RETCODE.OK, '注册成功')
    except Exception as e:
        db.session.rollback()
        result1 = re.search('Duplicate entry.*key.*username', str(e))
        result2 = re.search('Duplicate entry.*key.*phone', str(e))
        if result1 is not None:
            response_data = gen_response_data(RETCODE.EXCEPTION, '此用户名已经注册过，请更换用户名')
        elif result2 is not None:
            response_data = gen_response_data(RETCODE.EXCEPTION, '此手机号已经注册过，请更换手机号码')
            return jsonify(response_data)
        else:
            response_data = gen_response_data(RETCODE.EXCEPTION, '注册失败')
    return jsonify(response_data)


@bp.route("/login", methods=['POST'])
def login():
    username = request.json.get('username', '')
    password = request.json.get('password', '')
    if len(password) == 0 or len(username) == 0:
        response_data = gen_response_data(RETCODE.LOGINERR, '请输入用户名或手机号和密码')
        return jsonify(response_data)
    userbyusername = UserModel.query.filter(UserModel.username == username).first()
    userbyphone = UserModel.query.filter(UserModel.phone == username).first()
    user = userbyusername if userbyusername is not None else userbyphone
    if not user:
        response_data = gen_response_data(RETCODE.NOUSER, '未找到用户')
        return jsonify(response_data)
    if not check_password_hash(user.password, password):
        response_data = gen_response_data(RETCODE.PWDERR, '密码错误')
        return jsonify(response_data)
    token = jwt_encode({'uid': user.id, 'username': user.username})
    response_data = gen_response_data(RETCODE.OK, '登录成功', token=token)
    return jsonify(response_data)


@bp.route("/phone_login", methods=['POST'])
def phone_login():
    phone = request.json.get('phone', '')
    r_code = request.json.get('code', None)
    code = redis_store.get('valid_code:{}'.format(phone))
    if len(phone) == 0 or len(r_code) == 0:
        response_data = gen_response_data(RETCODE.LOGINERR, '请正确输入手机号或验证码')
        return jsonify(response_data)
    if code is None:
        response_data = gen_response_data(RETCODE.CODEEXPIRES, '验证码过期')
        return jsonify(response_data)
    if code != r_code:
        response_data = gen_response_data(RETCODE.CODEERR, '验证码错误')
        return jsonify(response_data)
    user = UserModel.query.filter(UserModel.phone == phone).first()
    if not user:
        response_data = gen_response_data(RETCODE.NOUSER, '未找到用户')
        return jsonify(response_data)
    token = jwt_encode({'uid': user.id, 'username': user.username})
    response_data = gen_response_data(RETCODE.OK, '登录成功', token=token)
    return jsonify(response_data)
