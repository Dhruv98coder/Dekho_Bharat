from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.chat_page,
        name="chat_page"
    ),

    path(
        "api/",
        views.chatbot_api,
        name="chatbot_api"
    ),

    path(
        "places/",
        views.places_api,
        name="places_api"
    ),

    path(
        "place/<path:place_name>/",
        views.place_detail_api,
        name="place_detail_api"
    ),
]