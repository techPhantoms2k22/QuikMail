from django.contrib import admin
from django.urls import path , include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path("logout/", views.logoutUser, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("message/<str:id>", views.seeMessage, name="message"),
    #Test
]