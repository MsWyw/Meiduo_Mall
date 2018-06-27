import re
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import *
from django_redis import get_redis_connection
from .utils import get_user_by_account


class CreateUserSerializer(serializers.ModelSerializer):
    """创建用户序列化器"""
    password2 = serializers.CharField(label="确认密码", required=True, allow_null=False, allow_blank=False, write_only=True)
    sms_code = serializers.CharField(label="短信验证码", required=True, allow_null=False, allow_blank=False, write_only=True)
    allow = serializers.CharField(label="同意协议", required=True, allow_null=False, allow_blank=True, write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)

    def validate_mobile(self, value):
        if re.match(r'^1[3-9]\d{9}$', value):
            return value
        else:
            raise serializers.ValidationError('您输入的手机号格式不正确')

    def validate_allow(self, value):
        if value == "true":
            return value
        else:
            raise serializers.ValidationError('请勾选同意')

    def validate(self, attrs):
        # 判断两次密码是否一致
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次输入的密码不一致')
        # 判断短信验证码是否正确
        mobile = attrs['mobile']
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        real_sms_code = real_sms_code.decode()
        if real_sms_code != attrs['sms_code']:
            raise serializers.ValidationError('短信验证码错误')
        return attrs

    def create(self, validated_data):
        """创建用户"""
        del validated_data['allow']
        del validated_data['password2']
        del validated_data['sms_code']
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        # 补充生成记录登陆状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user

    class Meta:
        model = User
        extra_kwargs = {
            'id': {"read_only": True},
            'username': {
                "min_length": 5,
                "max_length": 20,
                'error_messages': {
                    "max_length": "用户名必须为5到20位字符",
                    "min_length": "用户名必须为5到20位字符"
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                "error_messages": {
                    "max_length": '密码必须为5到20位字符',
                    'min_length': '密码必须为5到20位字符'
                }
            }
        }
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'allow', 'mobile', 'token')


class CheckSMSCodeSerializer(serializers.Serializer):
    """校验短信验证码的序列号器"""
    sms_code = serializers.CharField(min_length=6, max_length=6)

    def validate_sms_code(self, value):
        account = self.context['view'].kwargs.get("account")
        user = get_user_by_account(account)
        mobile = user.mobile
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile).decode()
        if real_sms_code is None:
            raise serializers.ValidationError('短信验证码无效')
        if value != real_sms_code:
            raise serializers.ValidationError('短信验证码错误')
        self.user = user
        return value


class CheckPasswordTokenSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(label='重置密码的access_token', write_only=True)
    password2 = serializers.CharField(label="确认密码", write_only=True)

    def validate(self, attrs):
        user_id = self.context['view'].kwargs.get('pk')
        access_token = attrs.get('access_token')
        print(attrs['password'])
        print(attrs['password2'])
        print(user_id)
        print(access_token)
        allow = User.check_password_code_token(access_token, user_id)
        print(allow)
        if not allow:
            raise serializers.ValidationError('无效的access_token')
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一样')
        return attrs

    def update(self, instance, validated_data):
        """更新密码"""
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('id', 'password', "password2", "access_token")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
                "max_length": 20,
                "error_messages": {
                    "min_length": '仅允许8-20个字符的密码',
                    "max_length": '仅允许8-20个字符的密码'
                }
            }
        }
