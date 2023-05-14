from django.contrib import admin
from django.urls import path , include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path("logout/", views.logoutUser, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("inbox/<str:id>/", views.seeInbox, name="seeInbox"),
    path("outbox/<str:id>/", views.seeOutbox, name="seeOutbox"),
    path("attachment/<str:id>/",views.attachmentContentDownload_Inbox,name="attachmentContent"),
    #Test
]
