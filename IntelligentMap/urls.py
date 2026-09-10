from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("goplan_home.urls")),
    path("map/", include("map_engine.urls")),
    path("shristi/", include("chatbot.urls")),
    path("metro/", include("metro.urls")),
    path("native/", include("native_language.urls")),
]
