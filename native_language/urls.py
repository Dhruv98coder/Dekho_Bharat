from django.urls import path
from . import views

app_name = "native_language"

urlpatterns = [
    path("", views.home, name="home"),
    path("detect/", views.detect, name="detect"),
    path("translate/", views.translate, name="translate"),
]
