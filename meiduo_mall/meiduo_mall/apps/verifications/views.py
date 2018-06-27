import random

from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http.response import HttpResponse

# Create your views here.
# from meiduo_mall.meiduo_mall.libs.captcha.captcha import captcha
from celery_tasks.sms.tasks import send_sms_code
from meiduo_mall.libs.captcha.captcha import captcha
from . import constants
from . import serlializers


class ImageCodeView(APIView):
    def get(self, request, image_code_id):
        """获取图片验证码"""
        # 生产验证码图片
        text, image = captcha.generate_captcha()
        # 获取redis连接对象，参数就是配置文件中的redistribute配置
        redis_conn = get_redis_connection('verify_codes')
        # 保存图片验证码到redistribute中
        # redis_conn.setex('变量名','有效期','值')
        redis_conn.setex('img_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return HttpResponse(image, content_type='image/jpg')


class SMSCodeView(GenericAPIView):
    serializer_class = serlializers.ImageCodeCheckSerializer

    def get(self, request, mobile):
        """获取短信验证码"""
        # 检查图片验证码
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 生产短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # 保存短信验证码与发送记录
        redis_conn = get_redis_connection('verify_codes')
        p1 = redis_conn.pipeline()
        p1.multi()
        p1.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        p1.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        p1.execute()
        send_sms_code.delay(mobile, sms_code)
        return Response({'message': "OK"}, status.HTTP_200_OK)


class FindPasswordSMSCodeView(GenericAPIView):
    serializer_class = serlializers.CheckAccessTokenForSMSSerializer

    def get(self, request):
        serlializer = self.get_serializer(data=request.query_params)
        serlializer.is_valid(raise_exception=True)
        mobile = serlializer.mobile
        # 生产短信验证码
        print(mobile)
        sms_code = '%06d' % random.randint(0, 999999)
        # 保存短信验证码与发送记录
        redis_conn = get_redis_connection('verify_codes')
        p1 = redis_conn.pipeline()
        p1.multi()
        p1.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        p1.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        p1.execute()
        send_sms_code.delay(mobile, sms_code)
        return Response({'message': "OK"}, status.HTTP_200_OK)

