import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import TripRecord

from .engine import get_place, get_popular_places, get_total_places, recommend_places


# =========================================================
# HOME
# =========================================================

def home(request):
    query = ""
    main_place = None
    recommendations = []
    popular_places = get_popular_places(top_k=8)


    # =====================================================
    # USER SEARCH
    # =====================================================

    if request.method == "POST":

        query = request.POST.get(
            "description",
            ""
        ).strip()


        if query:

            results = recommend_places(query, top_k=5)
            if results:
                main_place = results[0]
                recommendations = results[1:5]

    # Keep a useful recommendation visible before the first search too.
    if main_place is None and popular_places:
        main_place = popular_places[0]
        recommendations = popular_places[1:5]


    # =====================================================
    # CONTEXT
    # =====================================================

    user_name = "User"
    if getattr(request, "user", None) is not None and request.user.is_authenticated:
        user_name = request.user.get_full_name() or request.user.get_username() or "User"

    context = {
        "query": query,
        "main_place": main_place,
        "recommendations": recommendations,
        "popular_places": popular_places,
        "total_places": get_total_places(),
        "user_name": user_name,
    }
    context["active_module"] = "home"
    return render(request, "home.html", context)


def _trip_scope(request):
    if not request.session.session_key:
        request.session.save()
    return request.user if request.user.is_authenticated else request.session.session_key


def trip_history(request):
    return render(request, "trips/history.html", {"active_module": "history"})


@require_http_methods(["GET", "POST"])
def trips_api(request):
    scope = _trip_scope(request)
    qs = TripRecord.objects.filter(user=scope) if hasattr(scope, "pk") else TripRecord.objects.filter(session_key=scope)
    if request.method == "GET":
        return JsonResponse({"success": True, "trips": [
            {"id": t.id, "title": t.title, "origin": t.origin, "destination": t.destination,
             "mode": t.mode, "distance_km": float(t.distance_km) if t.distance_km is not None else None,
             "duration_minutes": t.duration_minutes, "created_at": t.created_at.isoformat()}
            for t in qs[:100]
        ]})
    try:
        data = json.loads(request.body or "{}")
        destination = str(data.get("destination", "")).strip()
        if not destination:
            return JsonResponse({"success": False, "error": "Destination is required."}, status=400)
        trip = TripRecord.objects.create(
            user=scope if hasattr(scope, "pk") else None,
            session_key="" if hasattr(scope, "pk") else scope,
            title=str(data.get("title") or f"Trip to {destination}")[:180],
            origin=str(data.get("origin") or "")[:180],
            destination=destination[:180], mode=str(data.get("mode") or "car")[:30],
            distance_km=data.get("distance_km"), duration_minutes=data.get("duration_minutes"),
            details=data.get("details") if isinstance(data.get("details"), dict) else {},
        )
        return JsonResponse({"success": True, "id": trip.id}, status=201)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=400)


@require_http_methods(["DELETE"])
def clear_trips(request):
    scope = _trip_scope(request)
    qs = TripRecord.objects.filter(user=scope) if hasattr(scope, "pk") else TripRecord.objects.filter(session_key=scope)
    qs.delete()
    return JsonResponse({"success": True})


@require_http_methods(["DELETE"])
def delete_trip(request, trip_id):
    scope = _trip_scope(request)
    qs = TripRecord.objects.filter(user=scope) if hasattr(scope, "pk") else TripRecord.objects.filter(session_key=scope)
    qs.filter(id=trip_id).delete()
    return JsonResponse({"success": True})



def place_detail(request):
    """Return a dataset place so the frontend can promote a clicked card."""
    name = request.GET.get("name", "").strip()
    print(name)
    place = get_place(name)
    if place is None:
        return JsonResponse({"error": "That place was not found in the dataset."}, status=404)
    recommendations = [
        candidate
        for candidate in recommend_places(place["name"], top_k=6)
        if candidate["name"].casefold() != place["name"].casefold()
    ][:4]
    response= JsonResponse({"place": place, "recommendations": recommendations})
    print(place)
    response["Access-Control_Allow-Origin"]='*'

    return response


def weather(request):
    """Proxy current Open-Meteo weather without exposing browser-side API plumbing."""
    try:
        latitude = float(request.GET.get("latitude", ""))
        longitude = float(request.GET.get("longitude", ""))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Valid place coordinates are required."}, status=400)

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return JsonResponse({"error": "Place coordinates are outside the valid range."}, status=400)

    query = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "is_day,precipitation,rain,weather_code,wind_speed_10m"
        ),
        "timezone": "auto",
    })
    request_url = f"https://api.open-meteo.com/v1/forecast?{query}"

    try:
        upstream_request = Request(
            request_url,
            headers={"User-Agent": "GoPlane/1.0 weather panel"},
        )
        with urlopen(upstream_request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        current = payload.get("current", {})
        units = payload.get("current_units", {})
        return JsonResponse({
            "time": current.get("time"),
            "timezone": payload.get("timezone"),
            "temperature": current.get("temperature_2m"),
            "temperature_unit": units.get("temperature_2m", "°C"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "rain": current.get("rain"),
            "weather_code": current.get("weather_code"),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_unit": units.get("wind_speed_10m", "km/h"),
            "is_day": current.get("is_day"),
        })
    except Exception:
        return JsonResponse(
            {"error": "Live weather is temporarily unavailable."},
            status=502,
        )