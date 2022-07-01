from datetime import timedelta

JSON_AS_ASCII = False
# 数据库的配置信息
HOSTNAME = 'bj-cynosdbmysql-grp-ifso5nx8.sql.tencentcdb.com'
PORT = '29050'
DATABASE = 'distillation'
USERNAME = 'devlop'
PASSWORD = 'ipmi123456!'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI

SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = "ipmidistillationkdyZRD7RdK5kXO0s"

# redis
REDIS_HOST = '124.223.222.243'
REDIS_PORT = 6379
REDIS_PWD = 'cnsoftbei'

# JWT
JWT_SECRET_KEY = ""
# JWT过期时间 48小时
JWT_EXPIRATION_DELTA = timedelta(seconds=3600*48)
JWT_VERIFY_CLAIMS = ['signature', 'exp', 'iat']
JWT_REQUIRED_CLAIMS = ['exp', 'iat']
JWT_AUTH_ENDPOINT = 'jwt'
JWT_ALGORITHM = 'HS256'
JWT_LEEWAY = timedelta(seconds=10)
JWT_AUTH_HEADER_PREFIX = 'JWT'
JWT_NOT_BEFORE_DELTA = timedelta(seconds=0)

# 腾讯云存储
secret_id = 'AKIDyoPmKekaBXdU6TaS5vWs0sUqvlLfisnT'
secret_key = 'SehX9ZpshHckfLl5JWYK3hQ2q0xq5JVV'
region = 'ap-chengdu'
token = None
scheme = 'https'

bucket = 'distillation-1312273849'

# 阿里云
AccessKey_ID = 'LTAI5tQi9guVXokvKH2h2GZb'
AccessKey_Secret = 'nThznxN2fE5aLiVZYavszeVT9pk7ZK'