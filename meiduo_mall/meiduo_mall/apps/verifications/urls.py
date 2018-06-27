from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'image_code/(?P<image_code_id>.*)/$', views.ImageCodeView.as_view()),
    url(r'sms_code/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
    url(r'sms_codes/$', views.FindPasswordSMSCodeView.as_view()),
    # JWT默认提供了登陆获取token的试图，可以直接使用；但是默认的返回值只有token，我们还需要自己添加username和user_id
    url(r'authorizations', obtain_jwt_token, name='authorizations')
]
