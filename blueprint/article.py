from flask import Blueprint, _request_ctx_stack
from exts import cos_client
from .decorators import jwt_required

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
    return "获取历史记录"
