import json
import numpy as np
import config
from tempfile import TemporaryFile
from flask import Blueprint, _request_ctx_stack, jsonify, request
from sqlalchemy import text, func
from blueprint import RETCODE
from exts import *
from models import ArticleModel
from .decorators import jwt_required
from .utils import JSONEncoder, gen_response_data
from PIL import Image
from docx import Document

bp = Blueprint('article', __name__, url_prefix="/api/article")


@bp.route("/ocr", methods=['POST'])
def generate_by_ocr():
    image_files = request.files.getlist('image')
    if not image_files:
        response_data = gen_response_data(RETCODE.PARAMERR, '请上传图片')
        return jsonify(response_data)
    try:
        text = ''
        for image_file in image_files:
            img = Image.open(image_file.stream).convert('RGB')
            img = np.array(img)
            result = ocr.ocr(img)
            for line in result:
                text += line[1][0]
        response_data = gen_response_data(RETCODE.OK, '抽取成功', title='title', abstract='abstract', text=text)
    except Exception as e:
        response_data = gen_response_data(RETCODE.EXCEPTION, '抽取失败')
    return jsonify(response_data)


@bp.route("/doc", methods=['POST'])
def generate_by_doc():
    doc_file = request.files.get('doc')
    if not doc_file:
        response_data = gen_response_data(RETCODE.PARAMERR, '请上传文档')
        return jsonify(response_data)
    try:
        temporary_file = TemporaryFile()
        temporary_file.write(doc_file.stream.read())
        temporary_file.seek(0)
        doc = Document(temporary_file)
        text = ''
        for para in doc.paragraphs:
            text += para.text
        response_data = gen_response_data(RETCODE.OK, '抽取成功', title='title', abstract='abstract', text=text)
    except Exception as e:
        response_data = gen_response_data(RETCODE.EXCEPTION, '抽取失败')
    return response_data


@bp.route("/text", methods=['POST'])
def generate_by_text():
    content = request.json.get('content')
    try:
        title, abstract = '', ''  # 由模型生成的摘要和标题
        response_data = gen_response_data(RETCODE.OK, '成功', title='title', abstract='abstract')
    except Exception as e:
        response_data = gen_response_data(RETCODE.EXCEPTION, '抽取失败')
    return jsonify(response_data)


@bp.route("/save", methods=['POST'])
@jwt_required
def save_result():
    user = _request_ctx_stack.top.current_identity
    content = request.json.get('content')
    title = request.json.get('title')
    abstract = request.json.get('abstract')
    try:
        history_count = \
            db.session.query(func.count(ArticleModel.id)).filter(ArticleModel.user_id == user['uid']).first()[0]
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
        response_data = gen_response_data(RETCODE.OK, '保存成功', article_id='article.id')
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # 数据库添加失败或云端保存失败时回滚
        response_data = gen_response_data(RETCODE.EXCEPTION, '保存失败')
    return jsonify(response_data)


@bp.route("/history", methods=['GET'])
@jwt_required
def get_history():
    user = _request_ctx_stack.top.current_identity
    try:
        articles = ArticleModel.query.filter(ArticleModel.user_id == user['uid']).order_by(text('-join_time')).all()
        data_json = json.loads(json.dumps(articles, cls=JSONEncoder))
        response_data = gen_response_data(RETCODE.OK, '查找成功', articles=data_json)
    except Exception as e:
        response_data = gen_response_data(RETCODE.EXCEPTION, '查找失败')
        return jsonify(response_data)
    return jsonify(response_data)


@bp.route("/detail/<id>/", methods=['GET'])
@jwt_required
def get_history_detail(id):
    remote_file = TemporaryFile()  # 创建临时文件
    article = ArticleModel.query.filter(ArticleModel.id == id).first()
    if not article:
        response_data = gen_response_data(RETCODE.NODETAIL, '未找到对应详情')
        return jsonify(response_data)
    try:
        # 从云端读取数据
        response = cos_client.get_object(  # 从云端获取对应文本数据
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
        data_json = json.loads(json.dumps(article, cls=JSONEncoder))
        data_json['text'] = text
        response_data = gen_response_data(RETCODE.OK, '获取成功', article=data_json)
    except Exception as e:
        response_data = gen_response_data(RETCODE.EXCEPTION, '获取失败')
        return jsonify(response_data)
    return jsonify(response_data)
