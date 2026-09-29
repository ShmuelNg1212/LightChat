from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("c/<int:pk>/", views.conversation, name="conversation"),
    path("c/<int:pk>/rename/", views.rename, name="rename"),
    path("c/<int:pk>/delete/", views.delete, name="delete"),
    path("send/", views.send, name="send"),
    path("g/<int:pk>/cancel/", views.cancel, name="cancel"),
]
