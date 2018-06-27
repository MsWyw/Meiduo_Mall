import re

from django.contrib.auth.backends import ModelBackend

from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """自定义jwt认证成功返回数据"""
    return {
        'token': token,
        'username': user.username,
        'user_id': user.id
    }


def get_user_by_account(account):
    """
    根据账号获取user对象
    :param account: 表示账号可以是用户名，也可以是手机号
    :return: User对象，或者None
    """
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            """表明输入账号为手机号"""
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义用户名或手机号认证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
