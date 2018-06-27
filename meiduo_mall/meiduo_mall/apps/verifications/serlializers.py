# 序列化
from rest_framework import serializers
from django_redis import get_redis_connection
import logging
from redis import RedisError

from users.models import User

# 获取在配置文件中定义的logger，用来记录日志
logger = logging.getLogger('meiduo')


class ImageCodeCheckSerializer(serializers.Serializer):
    """检查图片验证码"""
    # 声明验证规则
    image_code_id = serializers.UUIDField()
    image_code = serializers.CharField(max_length=4, min_length=4)

    # 编写验证代码 validate
    def validate(self, attrs):
        """校验"""
        image_code_id = attrs.get('image_code_id')
        image_code = attrs.get('image_code')
        # 从redis中获取真实的验证码
        redis_conn = get_redis_connection('verify_codes')
        real_image_code_text = redis_conn.get('img_%s' % image_code_id)

        if not real_image_code_text:
            raise serializers.ValidationError('图片验证码无效')

        try:
            # 删除一个不存在的键会报错
            redis_conn.delete()
        except RedisError as e:
            print(e)
            logger.error(e)

        real_image_code_text = real_image_code_text.decode()
        if real_image_code_text.lower() != image_code.lower():
            raise serializers.ValidationError('图片验证码错误')
        # 判断是否在60s内有效
        # 在序列化器中可以通过 self.context['view'].kwargs['参数名称']
        mobile = self.context['view'].kwargs.get('mobile')
        if mobile:
            send_flag = redis_conn.get('send_flag_%s' % mobile)
            if send_flag:
                raise serializers.ValidationError('请求次数频繁')
        # 返回验证数据
        return attrs


class CheckAccessTokenForSMSSerializer(serializers.Serializer):

    access_token = serializers.CharField(label='发送短信的临时票据access_token', allow_null=False, required=True)

    def validate(self, attrs):
        # 获取access_token
        access_token = attrs.get('access_token')
        # 验证access_token并获取其中的mobile
        mobile = User.check_sms_code_token(access_token)
        if not mobile:
            raise serializers.ValidationError('无效或错误的access_token')
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('请求次数过于频繁')

        self.mobile = mobile
        return attrs