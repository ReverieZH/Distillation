from flask import Blueprint, jsonify

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
