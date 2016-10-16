from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^request_static', views.request_static, name='req_st'),
    url(r'^request_dynamic', views.request_dynamic, name='req_dy'),
    url(r'^post_data', views.post_current_data, name='post_data')
]
