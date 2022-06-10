from flask import Blueprint, _request_ctx_stack, jsonify, request
from tempfile import TemporaryFile
from exts import cos_client
import config
from .decorators import jwt_required
from .utils import response_data, JSONEncoder
from blueprint import RETCODE
from models import ArticleModel
import json
from sqlalchemy import text
bp = Blueprint('article', __name__, url_prefix="/api/article")


@bp.route("/ocr")
def generate_by_ocr():
    return "由ocr方式抽取"


@bp.route("/doc")
def generate_by_doc():
    return "由doc方式抽取"


@bp.route("/text")
def generate_by_text():
    return "由文本方式抽取"


@bp.route("/history")
@jwt_required
def get_history():
    user = _request_ctx_stack.top.current_identity
    try:
        articles = ArticleModel.query.filter(ArticleModel.user_id == user['uid']).order_by(text('-join_time')).all()
        data_json = json.loads(json.dumps(articles, cls=JSONEncoder))
    except Exception as e:
        response_data['meta']['msg'] = '查找失败'
        response_data['meta']['status'] = RETCODE.EXCEPTION
        return jsonify(response_data)
    response_data['meta']['msg'] = '查找成功'
    response_data['meta']['status'] = RETCODE.OK
    response_data['data']['articles'] = data_json
    return jsonify(response_data)


@bp.route("/detail/<id>/")
@jwt_required
def get_history_detail(id):
    remote_file = TemporaryFile()
    article = ArticleModel.query.filter(ArticleModel.id == id).first()
    if not article:
        response_data['meta']['msg'] = '未找到对应详情'
        response_data['meta']['status'] = RETCODE.NODETAIL
        return jsonify(response_data)
    try:
        response = cos_client.get_object(
            Bucket=config.bucket,
            Key=article.filepath,
        )
        stream = response['Body'].get_raw_stream().read(1024)
        while stream:
            remote_file.write(stream)
            stream = response['Body'].get_raw_stream().read(1024)
        remote_file.seek(0)
        text = remote_file.read().decode('utf-8')
    except Exception as e:
        response_data['meta']['msg'] = '获取失败'
        response_data['meta']['status'] = RETCODE.EXCEPTION
        return jsonify(response_data)
    response_data['meta']['msg'] = '获取成功'
    response_data['meta']['status'] = RETCODE.OK
    data_json = json.loads(json.dumps(article, cls=JSONEncoder))
    data_json['text'] = text
    response_data['data']['article'] = data_json
    return jsonify(response_data)
