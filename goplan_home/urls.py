from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/place/", views.place_detail, name="place_detail"),
    path("api/weather/", views.weather, name="home_weather"),
    path("trips/", views.trip_history, name="trip_history"),
    path("api/trips/", views.trips_api, name="trips_api"),
    path("api/trips/clear/", views.clear_trips, name="clear_trips"),
    path("api/trips/<int:trip_id>/", views.delete_trip, name="delete_trip"),
]
