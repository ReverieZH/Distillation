from flask import Blueprint

bp = Blueprint('user', __name__, url_prefix="/api/user")


@bp.route("/login")
def login():
    return "登录"


@bp.route("/register")
def register():
    return "注册"
