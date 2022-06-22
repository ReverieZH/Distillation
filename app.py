from flask import Flask
from flask_cors import CORS
import config
from exts import db
from blueprint import article_bp, user_bp
from flask_migrate import Migrate
from models import *

app = Flask(__name__)
CORS(app)
# 配置信息
app.config.from_object(config)

# 初始化app
db.init_app(app)
# 注册蓝图
app.register_blueprint(article_bp)
app.register_blueprint(user_bp)

# 数据库迁移
migrate = Migrate(app, db)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
