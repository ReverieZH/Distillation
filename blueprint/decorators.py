# decorator.py
import jwt
from datetime import datetime
from functools import wraps
from werkzeug.local import LocalProxy
from flask import request, jsonify, _request_ctx_stack, current_app
from blueprint import RETCODE
import re

current_identity = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_identity', None))


def jwt_payload(identity):
    # 开始时间
    iat = datetime.utcnow()
    # 过期时间
    exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
    return {'exp': exp, 'iat': iat, 'identity': identity}


def jwt_encode(identity):
    secret = current_app.config['JWT_SECRET_KEY']
    algorithm = current_app.config['JWT_ALGORITHM']
    required_claims = current_app.config['JWT_REQUIRED_CLAIMS']
    payload = jwt_payload(identity)
    missing_claims = list(set(required_claims) - set(payload.keys()))
    if missing_claims:
        raise RuntimeError('Payload is missing required claims: %s' % ', '.join(missing_claims))
    return jwt.encode(payload, secret, algorithm=algorithm, headers=None)


def jwt_decode(token):
    secret = current_app.config['JWT_SECRET_KEY']
    algorithm = current_app.config['JWT_ALGORITHM']
    leeway = current_app.config['JWT_LEEWAY']
    verify_claims = current_app.config['JWT_VERIFY_CLAIMS']
    required_claims = current_app.config['JWT_REQUIRED_CLAIMS']
    options = {
        'verify_' + claim: True
        for claim in verify_claims
    }
    options.update({
        'require_' + claim: True
        for claim in required_claims
    })
    return jwt.decode(token, secret, options=options, algorithms=[algorithm], leeway=leeway)


def jwt_required(fn):
    @wraps(fn)
    def wapper(*args, **kwargs):
        auth_header_value = request.headers.get('Authorization', None)
        if not auth_header_value:
            return jsonify(code=RETCODE.NOAUTH, msg='Authorization缺失')
        parts = auth_header_value.split('.')
        if len(parts) == 1:
            return jsonify(code=RETCODE.NOTOKEN, msg='Token缺失')
        elif len(parts) > 3:
            return jsonify(code=RETCODE.TOKENERR, msg='Token无效')
        token = auth_header_value
        try:
            payload = jwt_decode(token)
        except jwt.InvalidTokenError as e:
            return jsonify(code=RETCODE.INVALID_TOKEN, msg=str(e))
        _request_ctx_stack.top.current_identity = payload.get('identity')
        if payload.get('identity') is None:
            return jsonify(code=RETCODE.NOLOGIN, msg='用户不存在')
        return fn(*args, **kwargs)

    return wapper


def register_required(fn):
    @wraps(fn)
    def wapper(*args, **kwargs):
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        confirm_password = request.json.get('confirm_password', None)
        phone = request.json.get('phone', None)
        r_code = request.json.get('code', None)
        if username is None or password is None or confirm_password is None or phone is None or r_code is None:
            return jsonify(code=RETCODE.PARAMERR, msg='您有信息未填写')
        phone_match = re.search(re.compile(r"1[356789]\d{9}"), phone)
        password_match = re.search(re.compile(r'[0-9a-zA-Z]{8,10}'), password)
        if phone_match is None:
            return jsonify(code=RETCODE.PARAMERR, msg='手机号格式不正确')
        if password_match is None:
            return jsonify(code=RETCODE.PARAMERR, msg='密码格式不正确,包含数字、大写或小写字母8到16位')
        return fn(*args, **kwargs)

    return wapper
