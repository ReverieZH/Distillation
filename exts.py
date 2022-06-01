from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
import config
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

db = SQLAlchemy()
redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)
cos_config = CosConfig(Region=config.region, SecretId=config.secret_id, SecretKey=config.secret_key, Token=config.token, Scheme=config.scheme)
cos_client = CosS3Client(cos_config)