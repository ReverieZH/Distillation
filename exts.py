from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
import config
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.auth.credentials import StsTokenCredential
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest

db = SQLAlchemy()
redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

cos_config = CosConfig(Region=config.region, SecretId=config.secret_id, SecretKey=config.secret_key, Token=config.token,
                       Scheme=config.scheme)
cos_client = CosS3Client(cos_config)

# 阿里云短信
credentials = AccessKeyCredential(config.AccessKey_ID, config.AccessKey_Secret)
# use STS Token
# credentials = StsTokenCredential('<your-access-key-id>', '<your-access-key-secret>', '<your-sts-token>')
client = AcsClient(region_id='cn-hangzhou', credential=credentials)

