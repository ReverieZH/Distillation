from flask import Blueprint, jsonify, request, make_response
from exts import *
from werkzeug.security import check_password_hash, generate_password_hash
from .decorators import jwt_encode, jwt_required, current_identity
from models import UserModel
from blueprint import RETCODE
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
import random

bp = Blueprint('user', __name__, url_prefix="/api/user")


@bp.route('/valid_code', methods=['POST'])
def valid_code():
    # 获取数据
    phone = request.args.get('phone')

    try:
        # 生成四位随机数字字母作为验证码
        code = random.sample('0123456789', 4)
        code = "".join(code)
        # 将验证码保存到redis中，第一个参数是key，第二个参数是value，第三个参数表示60秒后过期
        redis_store.set('valid_code:{}'.format(phone), code, 60)
        sms_request = SendSmsRequest()
        sms_request.set_accept_format('json')
        sms_request.set_SignName("阿里云短信测试")
        sms_request.set_TemplateCode("SMS_243280739")
        sms_request.set_PhoneNumbers(phone)
        sms_request.set_TemplateParam("{\"code\":\"%s\"}" % code)
        sms_response = client.do_action_with_exception(sms_request)
        # 这里用输出验证码来代替短信发送验证码
        return sms_response
    except Exception as e:
        return jsonify(status='失败', msg="验证码发送失败")


@bp.route("/register", methods=['POST'])
def register():
    return "注册"


@bp.route("/login", methods=['POST'])
def login():
    username = request.json.get('username', '')
    password = request.json.get('password', '')
    if len(username) == 0 or len(password) == 0:
        return jsonify(code=RETCODE.LOGINERR, msg='请输入正确的用户名或密码')
    user = UserModel.query.filter(UserModel.username == username).first()
    if not user:
        return jsonify(code=RETCODE.NOUSER, msg='未找到用户')
    if not check_password_hash(user.password, password):
        return jsonify(code=RETCODE.PWDERR, msg='密码错误')
    token = jwt_encode({'uid': user.id, 'username': user.username})
    return jsonify(code=RETCODE.OK, data={'token': token})
