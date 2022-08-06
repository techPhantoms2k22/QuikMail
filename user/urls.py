from django.contrib import admin
from django.urls import path , include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    # path("register/", views.register_request, name="register"),
    #Test
    path('test/',views.test,name='test'),
    path('test1/',views.test1,name='test1'),

]