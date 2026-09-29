from django.urls import path

from . import views

urlpatterns = [
    path("", views.credits_page, name="credits"),
    path("topup/", views.topup, name="topup"),
]
