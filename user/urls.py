from django.contrib import admin
from django.urls import path , include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path("logout/", views.logoutUser, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    #Test
    path('test/',views.test,name='test'),
    path('test1/',views.test1,name='test1'),

]