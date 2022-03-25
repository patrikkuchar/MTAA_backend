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
#from rest_framework_simplejwt import views as jwt_views
from app import views

urlpatterns = [
    #USER

    # [POST] ( REGISTER USER )
    path('user/register/', views.register_user, name='register_user'),

    # [POST] ( LOGIN USER )
    path('user/login/', views.login_user, name='login_user'),

    # FILTER

    # [POST] ( LOGIN USER )
    path('filter/<str:parameters>/', views.filter, name='filter'),






    # PROPERTY 

    # [GET] (Show info about property page)
    path('property/<int:property_id>/', views.property_info, name='property_info'),

    # [POST] (ADD new property to DATABASE)
    path('property/', views.property_add, name='property_add'),

    # [DELETE] (Delete property from DATABASE)
    path('property/<int:property_id>/delete/', views.property_delete, name='property_delete'),




    # BOOKINGS

    # [GET] Show all user's booking
    # [POST] Add booking
    path('booking/', views.booking_info_create, name='booking_info_create'),


    # [DELETE] Delete existing booking
    path('booking/<int:booking_id>/delete/', views.booking_delete, name='booking_delete'),




    # LIKED

    # [GET] Show all user's liked properties
    # [POST] Add property to user's liked list
    path('liked/', views.liked_info_create, name='liked_info_create'),
    
    # [DELETE] Remove property from user's liked list
    path('liked/<int:liked_id>/delete/', views.liked_remove, name='liked_remove'),








]


