from flask import Blueprint, _request_ctx_stack, jsonify, request
from tempfile import TemporaryFile
from exts import *
import config
from .decorators import jwt_required
from .utils import response_data, JSONEncoder
from blueprint import RETCODE
from models import ArticleModel
import json
from sqlalchemy import text, func

bp = Blueprint('article', __name__, url_prefix="/api/article")


@bp.route("/ocr")
def generate_by_ocr():
    return "由ocr方式抽取"


@bp.route("/doc")
def generate_by_doc():

    return "由doc方式抽取"


@bp.route("/text", methods=['POST'])
def generate_by_text():
    content = request.json.get('content')
    title, abstract = '', ''   # 由模型生成的摘要和标题

    response_data['meta']['msg'] = '生成成功'
    response_data['meta']['status'] = RETCODE.EXCEPTION
    response_data['data']['title'] = title
    response_data['data']['abstract'] = abstract
    return jsonify(response_data)


@bp.route("/save",  methods=['POST'])
@jwt_required
def save_result():
    user = _request_ctx_stack.top.current_identity
    content = request.json.get('content')
    title = request.json.get('title')
    abstract = request.json.get('abstract')
    try:
        history_count = db.session.query(func.count(ArticleModel.id)).filter(ArticleModel.user_id == user['uid']).first()[0]
        filepath = user["username"] + "/" + str(user["uid"]) + "_" + str(history_count + 1) + ".txt"
        article = ArticleModel(title=title, abstract=abstract, filepath=filepath, user_id=user["uid"])
        db.session.add(article)
        response = cos_client.put_object(
            Bucket=config.bucket,
            Body=str(content).encode('utf-8'),
            Key=filepath,
            StorageClass='STANDARD',
            ContentType='text/html; charset=utf-8'
        )
        response_data['meta']['msg'] = '保存成功'
        response_data['meta']['status'] = RETCODE.OK
        response_data['data']['article_id'] = article.id
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # 数据库添加失败或云端保存失败时回滚
        response_data['meta']['msg'] = '保存失败'
        response_data['meta']['status'] = RETCODE.EXCEPTION
    return jsonify(response_data)


@bp.route("/history", methods=['GET'])
@jwt_required
def get_history():
    user = _request_ctx_stack.top.current_identity
    try:
        articles = ArticleModel.query.filter(ArticleModel.user_id == user['uid']).order_by(text('-join_time')).all()
        data_json = json.loads(json.dumps(articles, cls=JSONEncoder))
        response_data['meta']['msg'] = '查找成功'
        response_data['meta']['status'] = RETCODE.OK
        response_data['data']['articles'] = data_json
    except Exception as e:
        response_data['meta']['msg'] = '查找失败'
        response_data['meta']['status'] = RETCODE.EXCEPTION
        return jsonify(response_data)
    return jsonify(response_data)


@bp.route("/detail/<id>/", methods=['GET'])
@jwt_required
def get_history_detail(id):
    remote_file = TemporaryFile()  # 创建临时文件
    article = ArticleModel.query.filter(ArticleModel.id == id).first()
    if not article:
        response_data['meta']['msg'] = '未找到对应详情'
        response_data['meta']['status'] = RETCODE.NODETAIL
        return jsonify(response_data)
    try:
        # 从云端读取数据
        response = cos_client.get_object(   # 从云端获取对应文本数据
            Bucket=config.bucket,
            Key=article.filepath,
        )
        stream = response['Body'].get_raw_stream().read(1024)
        while stream:
            remote_file.write(stream)
            stream = response['Body'].get_raw_stream().read(1024)
        remote_file.seek(0)
        text = remote_file.read().decode('utf-8')
        # 返回数据
        response_data['meta']['msg'] = '获取成功'
        response_data['meta']['status'] = RETCODE.OK
        data_json = json.loads(json.dumps(article, cls=JSONEncoder))
        data_json['text'] = text
        response_data['data']['article'] = data_json
    except Exception as e:
        response_data['meta']['msg'] = '获取失败'
        response_data['meta']['status'] = RETCODE.EXCEPTION
        return jsonify(response_data)
    return jsonify(response_data)
