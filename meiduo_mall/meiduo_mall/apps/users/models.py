from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer

# Create your models here.
from . import contants


class User(AbstractUser):
    """
    用户模型类
    """
    mobile = models.CharField(max_length=11, verbose_name="手机号码", unique=True)

    class Meta:
        db_table = "tb_users"
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def generate_sms_code_token(self):
        """生成发送短信验证码的token"""
        # TimedJSONWebSignatureSerializer(秘钥， token有效期[时间秒)
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, contants.SMS_CODE_TOKEN_EXPIRES)
        token = serializer.dumps({'mobile': self.mobile})
        token = token.decode()
        return token

    @staticmethod
    def check_sms_code_token(access_token):
        """校验发送短信的access_token"""
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, contants.SMS_CODE_TOKEN_EXPIRES)
        data = serializer.loads(access_token)
        mobile = data.get('mobile')
        return mobile

    def generate_password_token(self):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, contants.SMS_CODE_TOKEN_EXPIRES)
        data = serializer.dumps({'user_id': self.id})
        token = data.decode()
        return token

    @staticmethod
    def check_password_code_token(access_token, user_id):
        """校验发送密码的access_token"""
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, contants.SMS_CODE_TOKEN_EXPIRES)
        data = serializer.loads(access_token)
        print(data.get('user_id'))
        print("======")
        print(user_id)
        if int(user_id) == data.get('user_id'):
            return True
        return False
