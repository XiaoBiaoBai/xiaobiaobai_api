"""xiaobiaobai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from xiaobiaobai.admin_site import admin_site
from django.urls import path

from werobot.contrib.django import make_view
from weixin.robot import robot

from weixin import views

urlpatterns = [
    path('', views.get_wxuser_openid),
    path('admin/', admin_site.urls),
    path(r'wxcallback', make_view(robot)),
]
