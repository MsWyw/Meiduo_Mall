import re
from django.shortcuts import render

# Create your views here.
from rest_framework import status, mixins
from rest_framework.generics import CreateAPIView, GenericAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CheckSMSCodeSerializer
from . import serializers
from .models import User
from .utils import get_user_by_account
from verifications.serlializers import ImageCodeCheckSerializer


class UserMobileCodeView(APIView):
    """校验用户手机号码是否存在"""
    def get(self, request, mobile):
        count = User.objects.filter(mobile__exact=mobile).count()
        data = {
            "mobile": mobile,
            "count": count
        }
        return Response(data)


class UserNameCodeView(APIView):
    """校验用户名是否存在"""
    def get(self, request, username):
        count = User.objects.filter(username__exact=username).count()
        print(count)
        data = {
            "username": username,
            "count": count
        }
        return Response(data)


class UsersView(CreateAPIView):
    """用户注册"""
    serializer_class = serializers.CreateUserSerializer


class CheckImageCodeSerializer(GenericAPIView):
    """找回密码第一步验证图片验证码和账号"""
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, account):
        # 1.验证账号
        user = get_user_by_account(account)
        if user is None:
            return Response({"message": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        # 2.验证图片验证码
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 3.生成access_token凭证并返回给前端
        assess_token = user.generate_sms_code_token()
        mobile = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1好好学习\2', user.mobile)
        return Response({'mobile': mobile, "access_token": assess_token})


class PasswordTokenView(GenericAPIView):
    serializer_class = serializers.CheckSMSCodeSerializer

    def get(self, request, account):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        assess_token = user.generate_password_token()
        return Response({'access_token': assess_token, "user_id": user.id}, status=status.HTTP_200_OK)


class PasswordView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.CheckPasswordTokenSerializer

    def post(self, request, pk):
        return self.update(request, pk)
