"""MTAA_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('test/', views.postTest, name='postTest'),


    # USERS ( REGISTER USER )
    path('user/', views.register_user, name='register_user'),

    # USER ( LOGIN USER )
    path('user/<str:email>/', views.login_user, name='login_user'),


    # PROPERTY (Show info about property page)
    path('property/<int:property_id>/', views.property_info, name='property_info'),

    # PROPERTY (ADD new property to DATABASE)
    path('property/', views.property_add, name='property_add'),

]


