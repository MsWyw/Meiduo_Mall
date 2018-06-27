from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.UserMobileCodeView.as_view()),
    url(r'^username/(?P<username>\w{5,20})/count/$', views.UserNameCodeView.as_view()),
    # url(r'^users/$', views.UsersView.as_view()),
    url(r'^users_register/$', views.UsersView.as_view()),
    url(r'^accounts/(?P<account>\w{5,20})/sms/token/$', views.CheckImageCodeSerializer.as_view()),
    url(r'^accounts/(?P<account>\w{5,20})/password/token/$', views.PasswordTokenView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token, name='authorizations'),
    url(r'^users/(?P<pk>\d+)/password/$', views.PasswordView.as_view())
]