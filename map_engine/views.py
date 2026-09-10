import csv
import json
import math
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime

import requests

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


# ============================================================
# CONFIG
# ============================================================

OSRM_URL = "https://router.project-osrm.org/route/v1"

BIKE_ROUTER_URL = os.getenv(
    "GOPLAN_BIKE_ROUTER_URL",
    "https://routing.openstreetmap.de/routed-bike/route/v1/driving",
)

FOOT_ROUTER_URL = os.getenv(
    "GOPLAN_FOOT_ROUTER_URL",
    "https://routing.openstreetmap.de/routed-foot/route/v1/driving",
)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
PHOTON_URL = "https://photon.komoot.io/api/"

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

USER_AGENT = os.getenv(
    "GOPLAN_USER_AGENT",
    "GoPlan-IntelligentMap/9.0",
)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_PATH = os.path.join(
    os.path.dirname(BASE_DIR),
    "dataset",
    "GoPlan_Delhi_Places_AI_Dataset_READABLE(final).csv",
)

# south, west, north, east
NCR_BBOX = (
    28.20,
    76.65,
    29.10,
    77.85,
)


# ============================================================
# BASIC HELPERS
# ============================================================

def _json_request(
    url,
    method="GET",
    data=None,
    headers=None,
    timeout=15,
):
    body = None

    request_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }

    if headers:
        request_headers.update(headers)

    if data is not None:

        content_type = request_headers.get(
            "Content-Type",
            "",
        ).lower()

        if isinstance(data, str):
            body = data.encode("utf-8")

        elif (
            "application/x-www-form-urlencoded"
            in content_type
        ):
            body = urllib.parse.urlencode(
                data
            ).encode("utf-8")

        elif "text/plain" in content_type:
            body = str(data).encode("utf-8")

        else:
            body = json.dumps(
                data
            ).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers=request_headers,
        method=method,
    )

    with urllib.request.urlopen(
        req,
        timeout=timeout,
    ) as response:

        return json.loads(
            response.read().decode(
                "utf-8"
            )
        )


def _in_ncr(lat, lon):
    return (
        NCR_BBOX[0] <= lat <= NCR_BBOX[2]
        and NCR_BBOX[1] <= lon <= NCR_BBOX[3]
    )


def _distance_km(
    lat1,
    lon1,
    lat2,
    lon2,
):
    r = 6371.0088

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dlat = math.radians(
        lat2 - lat1
    )

    dlon = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dlon / 2) ** 2
    )

    return (
        r
        * 2
        * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )
    )


def _format_duration(seconds):
    minutes = max(
        0,
        round(
            float(seconds or 0) / 60
        ),
    )

    if minutes >= 60:
        return (
            f"{minutes // 60} hr "
            f"{minutes % 60:02d} min"
        )

    return f"{minutes} min"


# ============================================================
# NCR LOCALITY INDEX
# ============================================================

NCR_LOCALITIES = [
    ("New Delhi", 28.6139, 77.2090, "City"),
    ("Old Delhi", 28.6562, 77.2410, "City area"),
    ("Delhi", 28.7041, 77.1025, "City"),
    ("Dwarka", 28.5921, 77.0460, "Sub-city"),
    ("Rohini", 28.7495, 77.0565, "Locality"),
    ("Saket", 28.5245, 77.2066, "Locality"),
    ("Vasant Kunj", 28.5200, 77.1590, "Locality"),
    ("Karol Bagh", 28.6519, 77.1909, "Locality"),
    ("Pitampura", 28.6980, 77.1315, "Locality"),
    ("Ghaziabad", 28.6692, 77.4538, "City"),
    ("Duhai", 28.7717, 77.5230, "Town"),
    ("Vaishali", 28.6469, 77.3389, "Locality"),
    ("Indirapuram", 28.6461, 77.3720, "Locality"),
    ("Vasundhara", 28.6603, 77.3576, "Locality"),
    ("Noida", 28.5355, 77.3910, "City"),
    ("Greater Noida", 28.4744, 77.5040, "City"),
    ("Gurugram", 28.4595, 77.0266, "City"),
    ("Faridabad", 28.4089, 77.3178, "City"),
    ("Meerut", 28.9845, 77.7064, "City"),
    ("Hapur", 28.7306, 77.7759, "City"),
    ("Baghpat", 28.9440, 77.2189, "City"),
    ("Sikandrabad", 28.4524, 77.6992, "Town"),
    ("Khurja", 28.2526, 77.8513, "City"),
    ("Sonipat", 28.9931, 77.0151, "City"),
]

NCR_ALIASES = {
    "dilli": "Delhi",
    "puranidilli": "Old Delhi",
    "gaziabad": "Ghaziabad",
    "gaziyabad": "Ghaziabad",
    "ghaziyabad": "Ghaziabad",
    "ghaziabd": "Ghaziabad",
    "gurgaon": "Gurugram",
    "gurgoan": "Gurugram",
    "gurgao": "Gurugram",
    "faridbad": "Faridabad",
    "greaternoida": "Greater Noida",
}


# ============================================================
# DATASET
# ============================================================

def _load_dataset_places():

    if not os.path.exists(DATASET_PATH):
        print(
            "[GoPlan] Dataset not found:",
            DATASET_PATH,
        )
        return []

    places = []

    try:

        with open(
            DATASET_PATH,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                try:

                    lat = float(
                        row.get(
                            "latitude"
                        )
                        or row.get(
                            "destination_latitude"
                        )
                    )

                    lon = float(
                        row.get(
                            "longitude"
                        )
                        or row.get(
                            "destination_longitude"
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    continue

                if not _in_ncr(
                    lat,
                    lon,
                ):
                    continue

                places.append(
                    {
                        "name": (
                            row.get(
                                "place_name"
                            )
                            or row.get(
                                "name"
                            )
                            or "Place"
                        ),
                        "category": (
                            row.get(
                                "category"
                            )
                            or row.get(
                                "broad_category"
                            )
                            or "Tourist place"
                        ),
                        "latitude": lat,
                        "longitude": lon,
                        "description": (
                            row.get(
                                "description"
                            )
                            or ""
                        ),
                        "rating": (
                            row.get(
                                "rating"
                            )
                            or ""
                        ),
                        "best_time": (
                            row.get(
                                "best_time_suggestion"
                            )
                            or row.get(
                                "best_time_season"
                            )
                            or ""
                        ),
                        "awareness_tips": (
                            row.get(
                                "awareness_tips"
                            )
                            or ""
                        ),
                        "entry_fee": (
                            row.get(
                                "entry_fee_indian"
                            )
                            or row.get(
                                "entry_fee_foreigner"
                            )
                            or ""
                        ),
                        "source": "GoPlan dataset",
                    }
                )

    except Exception as error:

        print(
            "[GoPlan] Dataset error:",
            error,
        )

        return []

    return places


# ============================================================
# HOME
# ============================================================

@ensure_csrf_cookie
def map_home(request):

    return render(
        request,
        "map_engine/map.html",
        {
            "active_module": "map"
        },
    )


# ============================================================
# ROUTING
# ============================================================

def _route(
    profile,
    start,
    end,
):

    coords = (
        f"{start['longitude']},"
        f"{start['latitude']};"
        f"{end['longitude']},"
        f"{end['latitude']}"
    )

    if profile == "bike":
        base = BIKE_ROUTER_URL

    elif profile == "foot":
        base = FOOT_ROUTER_URL

    else:
        base = (
            f"{OSRM_URL}/driving"
        )

    params = urllib.parse.urlencode(
        {
            "alternatives": "2",
            "steps": "true",
            "geometries": "geojson",
            "overview": "full",
        }
    )

    return _json_request(
        f"{base}/{coords}?{params}",
        timeout=25,
    )


def _clean_route(
    route,
    index,
):

    steps = []

    for leg in route.get(
        "legs",
        [],
    ):

        for step in leg.get(
            "steps",
            [],
        ):

            maneuver = step.get(
                "maneuver",
                {},
            )

            location = maneuver.get(
                "location",
                [0, 0],
            )

            steps.append(
                {
                    "instruction": (
                        step.get(
                            "name"
                        )
                        or "Continue"
                    ),
                    "type": maneuver.get(
                        "type",
                        "",
                    ),
                    "modifier": maneuver.get(
                        "modifier",
                        "",
                    ),
                    "distance_m": round(
                        step.get(
                            "distance",
                            0,
                        )
                    ),
                    "duration_min": round(
                        step.get(
                            "duration",
                            0,
                        )
                        / 60
                    ),
                    "location": [
                        location[1],
                        location[0],
                    ],
                }
            )

    distance = route.get(
        "distance",
        0,
    )

    duration = route.get(
        "duration",
        0,
    )

    return {
        "index": index,
        "geometry": route.get(
            "geometry"
        ),
        "distance_km": round(
            distance / 1000,
            2,
        ),
        "distance_text": (
            f"{distance / 1000:.1f} km"
        ),
        "duration_minutes": round(
            duration / 60
        ),
        "duration_text": (
            _format_duration(
                duration
            )
        ),
        "steps": steps[:80],
    }


def calculate_route(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "error": "POST required",
            },
            status=405,
        )

    try:

        payload = json.loads(
            request.body
        )

        start = payload["from"]
        destination = payload["to"]

        start_point = {
            "latitude": float(
                start["latitude"]
            ),
            "longitude": float(
                start["longitude"]
            ),
        }

        end_point = {
            "latitude": float(
                destination["latitude"]
            ),
            "longitude": float(
                destination["longitude"]
            ),
        }

        mode = str(
            payload.get(
                "mode",
                "car",
            )
        ).lower()

    except (
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Invalid coordinates"
                ),
            },
            status=400,
        )

    profiles = {
        "car": "car",
        "bike": "bike",
        "foot": "foot",
    }

    if mode not in profiles:

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Use Metro planner for metro "
                    "and Rail planner for trains."
                ),
            },
            status=400,
        )

    if not (
        _in_ncr(
            start_point["latitude"],
            start_point["longitude"],
        )
        and
        _in_ncr(
            end_point["latitude"],
            end_point["longitude"],
        )
    ):

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Road navigation is available "
                    "inside Delhi NCR only."
                ),
            },
            status=400,
        )

    try:

        routing = _route(
            profiles[mode],
            start_point,
            end_point,
        )

    except Exception as error:

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Road routing unavailable: "
                    f"{error}"
                ),
            },
            status=502,
        )

    routes = [
        _clean_route(
            route,
            index,
        )
        for index, route in enumerate(
            routing.get(
                "routes",
                [],
            )[:3]
        )
    ]

    if not routes:

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "No road route found."
                ),
            },
            status=404,
        )

    return JsonResponse(
        {
            "success": True,
            "mode": mode,
            "routes": routes,
            "route": routes[0],
        }
    )


# ============================================================
# SEARCH
# ============================================================

def _normalise_query(query):

    value = re.sub(
        r"\s+",
        " ",
        str(query or "").strip(),
    )

    compact = re.sub(
        r"[^a-z0-9]",
        "",
        value.lower(),
    )

    return NCR_ALIASES.get(
        compact,
        value,
    )


def _nominatim_search(query):

    params = urllib.parse.urlencode(
        {
            "q": query,
            "format": "jsonv2",
            "limit": 8,
            "addressdetails": 1,
            "namedetails": 1,
            "countrycodes": "in",
            "accept-language": "en",
        }
    )

    return _json_request(
        f"{NOMINATIM_URL}?{params}",
        headers={
            "User-Agent": USER_AGENT
        },
        timeout=6,
    )


def search_places(request):

    q = re.sub(
        r"\s+",
        " ",
        request.GET.get(
            "q",
            "",
        ).strip(),
    )

    if len(q) < 2:

        return JsonResponse(
            {
                "results": [],
                "query": q,
                "scope": "Delhi NCR",
            }
        )

    query = _normalise_query(
        q
    )

    low = query.lower()

    results = []

    # Metro index
    try:

        from metro.services.station_search import (
            StationSearch
        )

        for station in StationSearch().search(
            query,
            top_k=8,
        ):

            results.append(
                {
                    "name": station["name"],
                    "display_name": (
                        f"{station['name']} "
                        "• Delhi NCR Metro"
                    ),
                    "latitude": station["latitude"],
                    "longitude": station["longitude"],
                    "category": "Metro station",
                    "source": "DMRC dataset",
                    "_score": 9000,
                }
            )

    except Exception as error:

        print(
            "[Search] Metro search skipped:",
            error,
        )

    # Localities
    for name, lat, lon, category in NCR_LOCALITIES:

        if low in name.lower():

            results.append(
                {
                    "name": name,
                    "display_name": (
                        f"{name} • Delhi NCR"
                    ),
                    "latitude": lat,
                    "longitude": lon,
                    "category": category,
                    "source": (
                        "GoPlan locality index"
                    ),
                    "_score": 8500,
                }
            )

    # Own dataset
    tokens = [
        token
        for token in re.findall(
            r"[a-z0-9]+",
            low,
        )
        if len(token) > 1
    ]

    for place in _load_dataset_places():

        text = (
            f"{place['name']} "
            f"{place['category']} "
            f"{place['description']}"
        ).lower()

        if (
            low in text
            or (
                tokens
                and any(
                    token in text
                    for token in tokens
                )
            )
        ):

            results.append(
                {
                    **place,
                    "display_name": (
                        f"{place['name']} • GoPlan"
                    ),
                    "_score": 8000,
                }
            )

    # Remote only on explicit request
    if request.GET.get(
        "remote"
    ) == "1":

        try:

            remote = _nominatim_search(
                query
            )

            for item in remote:

                try:

                    lat = float(
                        item["lat"]
                    )

                    lon = float(
                        item["lon"]
                    )

                except (
                    KeyError,
                    ValueError,
                    TypeError,
                ):
                    continue

                if not _in_ncr(
                    lat,
                    lon,
                ):
                    continue

                name = (
                    item.get("name")
                    or item.get(
                        "display_name",
                        "Place",
                    ).split(",")[0]
                )

                results.append(
                    {
                        "name": name,
                        "display_name": item.get(
                            "display_name",
                            name,
                        ),
                        "latitude": lat,
                        "longitude": lon,
                        "category": item.get(
                            "type",
                            "place",
                        ),
                        "source": (
                            "OpenStreetMap"
                        ),
                        "_score": 5000,
                    }
                )

        except Exception as error:

            print(
                "[Search] Nominatim failed:",
                error,
            )

    # Deduplicate
    output = []
    seen = set()

    for item in sorted(
        results,
        key=lambda x: -x.get(
            "_score",
            0,
        ),
    ):

        try:

            key = (
                round(
                    float(
                        item["latitude"]
                    ),
                    5,
                ),
                round(
                    float(
                        item["longitude"]
                    ),
                    5,
                ),
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            continue

        if key in seen:
            continue

        seen.add(key)
        item.pop(
            "_score",
            None,
        )
        output.append(
            item
        )

    return JsonResponse(
        {
            "results": output[:30],
            "query": q,
            "scope": "Delhi NCR",
        }
    )


# ============================================================
# NEARBY
# ============================================================

NEARBY_QUERIES = {

    "metro": [
        'nwr["railway"="station"]["station"="subway"]',
        'nwr["railway"="station"]["subway"="yes"]',
        'nwr["public_transport"="station"]["subway"="yes"]',
        'nwr["railway"="subway_entrance"]',
        'nwr["railway"="tram_stop"]',
    ],

    "train": [
        'nwr["railway"="station"]',
        'nwr["railway"="halt"]',
        'nwr["railway"="stop"]',
    ],

    "food": [
        'nwr["amenity"="restaurant"]',
        'nwr["amenity"="cafe"]',
        'nwr["amenity"="fast_food"]',
        'nwr["amenity"="food_court"]',
    ],

    "hotel": [
        'nwr["tourism"="hotel"]',
        'nwr["tourism"="hostel"]',
        'nwr["tourism"="guest_house"]',
        'nwr["tourism"="motel"]',
    ],

    "hospital": [
        'nwr["amenity"="hospital"]',
        'nwr["healthcare"="hospital"]',
    ],

    "pharmacy": [
        'nwr["amenity"="pharmacy"]',
        'nwr["healthcare"="pharmacy"]',
    ],

    "atm": [
        'nwr["amenity"="atm"]',
    ],

    "tourist": [
        'nwr["tourism"="attraction"]',
        'nwr["tourism"="museum"]',
        'nwr["tourism"="gallery"]',
        'nwr["tourism"="viewpoint"]',
        'nwr["tourism"="zoo"]',
        'nwr["tourism"="theme_park"]',
        'nwr["historic"]',
        'nwr["leisure"="park"]',
    ],
}


def _build_nearby_query(
    category,
    radius,
    lat,
    lon,
):
    selectors = NEARBY_QUERIES.get(
        category,
        NEARBY_QUERIES["tourist"],
    )

    parts = []

    for selector in selectors:
        parts.append(
            f"{selector}"
            f"(around:{radius},{lat},{lon});"
        )

    return (
        "[out:json][timeout:15];"
        "("
        + "".join(parts)
        + ")"
        "out center tags;"
    )


def _overpass_request(
    query,
    timeout=14,
):
    """
    Stable Overpass:
    GET -> POST -> next server.

    We do NOT allow one dead server to block Nearby forever.
    """

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }

    for server in OVERPASS_SERVERS:

        # GET
        try:

            response = requests.get(
                server,
                params={
                    "data": query
                },
                headers=headers,
                timeout=timeout,
            )

            if response.status_code == 200:

                data = response.json()

                if isinstance(
                    data,
                    dict,
                ):
                    print(
                        "[Nearby] Overpass GET OK:",
                        server,
                    )
                    return data

            print(
                "[Nearby] Overpass GET",
                server,
                "HTTP",
                response.status_code,
            )

        except Exception as error:

            print(
                "[Nearby] Overpass GET failed:",
                server,
                error,
            )

        # POST fallback
        try:

            response = requests.post(
                server,
                data={
                    "data": query
                },
                headers=headers,
                timeout=timeout,
            )

            if response.status_code == 200:

                data = response.json()

                if isinstance(
                    data,
                    dict,
                ):
                    print(
                        "[Nearby] Overpass POST OK:",
                        server,
                    )
                    return data

            print(
                "[Nearby] Overpass POST",
                server,
                "HTTP",
                response.status_code,
            )

        except Exception as error:

            print(
                "[Nearby] Overpass POST failed:",
                server,
                error,
            )

    return None


# ============================================================
# METRO DATASET FALLBACK
# ============================================================

def _nearby_metro_from_dataset(
    lat,
    lon,
    radius_m,
):
    results = []

    try:

        from metro.services.station_search import (
            StationSearch
        )

        stations = StationSearch().search(
            "",
            top_k=500,
        )

        for station in stations:

            try:

                station_lat = float(
                    station["latitude"]
                )

                station_lon = float(
                    station["longitude"]
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

            distance = (
                _distance_km(
                    lat,
                    lon,
                    station_lat,
                    station_lon,
                )
                * 1000
            )

            if distance > radius_m:
                continue

            results.append(
                {
                    "name": station["name"],
                    "latitude": station_lat,
                    "longitude": station_lon,
                    "distance_m": round(
                        distance
                    ),
                    "category": (
                        "Metro station"
                    ),
                    "source": (
                        "DMRC dataset"
                    ),
                }
            )

    except Exception as error:

        print(
            "[Nearby] Metro dataset fallback failed:",
            error,
        )

    results.sort(
        key=lambda x: x[
            "distance_m"
        ]
    )

    return results[:40]


# ============================================================
# PHOTON FALLBACK
# ============================================================

def _photon_search(
    category,
    lat,
    lon,
    radius_m,
):
    query_map = {
        "metro": "metro station",
        "train": "railway station",
        "food": "restaurant",
        "hotel": "hotel",
        "hospital": "hospital",
        "pharmacy": "pharmacy",
        "atm": "ATM",
        "tourist": "tourist attraction",
    }

    query = query_map.get(
        category,
        category,
    )

    try:

        response = requests.get(
            PHOTON_URL,
            params={
                "q": query,
                "lat": lat,
                "lon": lon,
                "limit": 40,
            },
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
            timeout=10,
        )

        if response.status_code != 200:
            return []

        data = response.json()

    except Exception as error:

        print(
            "[Nearby] Photon failed:",
            error,
        )
        return []

    results = []

    for feature in data.get(
        "features",
        [],
    ):

        geometry = feature.get(
            "geometry",
            {},
        )

        coords = geometry.get(
            "coordinates",
            [],
        )

        if len(coords) < 2:
            continue

        try:

            item_lon = float(
                coords[0]
            )

            item_lat = float(
                coords[1]
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        distance = (
            _distance_km(
                lat,
                lon,
                item_lat,
                item_lon,
            )
            * 1000
        )

        if distance > radius_m:
            continue

        props = feature.get(
            "properties",
            {},
        ) or {}

        name = (
            props.get("name")
            or props.get("street")
            or props.get("locality")
        )

        if not name:
            continue

        address = " ".join(
            str(value)
            for value in (
                props.get("street"),
                props.get("district"),
                props.get("city"),
            )
            if value
        )

        results.append(
            {
                "name": str(name),
                "latitude": item_lat,
                "longitude": item_lon,
                "distance_m": round(
                    distance
                ),
                "category": (
                    category.title()
                ),
                "address": address,
                "phone": "",
                "website": "",
                "opening_hours": "",
                "source": (
                    "OpenStreetMap / Photon"
                ),
            }
        )

    results.sort(
        key=lambda x: x[
            "distance_m"
        ]
    )

    return results[:40]


# ============================================================
# NEARBY ELEMENT PROCESSOR
# ============================================================

def _element_position(element):

    lat = element.get(
        "lat"
    )

    lon = element.get(
        "lon"
    )

    if lat is None or lon is None:

        center = element.get(
            "center",
            {},
        ) or {}

        lat = center.get(
            "lat"
        )

        lon = center.get(
            "lon"
        )

    try:

        return (
            float(lat),
            float(lon),
        )

    except (
        TypeError,
        ValueError,
    ):

        return (
            None,
            None,
        )


def _process_nearby_elements(
    elements,
    category,
    lat,
    lon,
    radius_m,
):
    results = []

    for element in elements:

        tags = element.get(
            "tags",
            {}
        ) or {}

        name = (
            tags.get("name")
            or tags.get("name:en")
            or tags.get("official_name")
            or tags.get("brand")
        )

        if not name:
            continue

        item_lat, item_lon = (
            _element_position(
                element
            )
        )

        if (
            item_lat is None
            or item_lon is None
        ):
            continue

        distance = (
            _distance_km(
                lat,
                lon,
                item_lat,
                item_lon,
            )
            * 1000
        )

        if distance > radius_m:
            continue

        results.append(
            {
                "name": str(name),
                "latitude": item_lat,
                "longitude": item_lon,
                "distance_m": round(
                    distance
                ),
                "category": (
                    category.title()
                ),
                "address": (
                    tags.get("addr:full")
                    or tags.get(
                        "addr:street"
                    )
                    or tags.get(
                        "addr:city"
                    )
                    or ""
                ),
                "phone": (
                    tags.get("phone")
                    or tags.get(
                        "contact:phone"
                    )
                    or ""
                ),
                "website": (
                    tags.get("website")
                    or tags.get(
                        "contact:website"
                    )
                    or ""
                ),
                "opening_hours": (
                    tags.get(
                        "opening_hours",
                        "",
                    )
                ),
                "source": (
                    "OpenStreetMap"
                ),
            }
        )

    return results


# ============================================================
# BUS STOP
# ============================================================

def _nearest_bus_stop(
    lat,
    lon,
    radius=1800,
):

    query = f"""
    [out:json][timeout:10];
    (
      nwr["highway"="bus_stop"]
      (around:{radius},{lat},{lon});

      nwr["public_transport"="platform"]
      ["bus"="yes"]
      (around:{radius},{lat},{lon});
    );
    out center tags;
    """

    data = _overpass_request(
        query,
        timeout=10,
    )

    if not data:
        return None

    best = None

    for element in data.get(
        "elements",
        [],
    ):

        tags = element.get(
            "tags",
            {}
        ) or {}

        name = (
            tags.get("name")
            or "Bus stop"
        )

        item_lat, item_lon = (
            _element_position(
                element
            )
        )

        if (
            item_lat is None
            or item_lon is None
        ):
            continue

        distance = (
            _distance_km(
                lat,
                lon,
                item_lat,
                item_lon,
            )
            * 1000
        )

        if (
            best is None
            or distance
            < best["distance_m"]
        ):

            best = {
                "name": name,
                "latitude": item_lat,
                "longitude": item_lon,
                "distance_m": round(
                    distance
                ),
            }

    return best


# ============================================================
# NEARBY API
# ============================================================

def nearby_places(request):

    if request.method != "GET":

        return JsonResponse(
            {
                "success": False,
                "results": [],
                "error": (
                    "GET request required"
                ),
            },
            status=405,
        )

    try:

        lat = float(
            request.GET.get(
                "lat"
            )
        )

        lon = float(
            request.GET.get(
                "lon"
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        return JsonResponse(
            {
                "success": False,
                "results": [],
                "error": (
                    "Valid latitude and longitude required."
                ),
            },
            status=400,
        )

    if not (
        -90 <= lat <= 90
        and -180 <= lon <= 180
    ):

        return JsonResponse(
            {
                "success": False,
                "results": [],
                "error": (
                    "Invalid geographic coordinates."
                ),
            },
            status=400,
        )

    category = (
        request.GET.get(
            "type"
        )
        or request.GET.get(
            "category"
        )
        or "tourist"
    ).lower().strip()

    if category not in NEARBY_QUERIES:

        return JsonResponse(
            {
                "success": False,
                "results": [],
                "error": (
                    "Unsupported nearby category."
                ),
            },
            status=400,
        )

    try:

        radius = int(
            request.GET.get(
                "radius",
                "25000",
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        radius = 25000

    # 1 km -> 25 km
    radius = max(
        1000,
        min(
            radius,
            25000,
        ),
    )

    print(
        f"[Nearby] Searching {category} "
        f"around {lat},{lon} "
        f"within {radius}m"
    )

    results = []
    seen = set()

    # ========================================================
    # 1. OWN GOPLAN DATASET
    # ========================================================

    if category == "tourist":

        for place in _load_dataset_places():

            distance = (
                _distance_km(
                    lat,
                    lon,
                    place["latitude"],
                    place["longitude"],
                )
                * 1000
            )

            if distance > radius:
                continue

            key = (
                round(
                    place["latitude"],
                    5,
                ),
                round(
                    place["longitude"],
                    5,
                ),
            )

            if key in seen:
                continue

            seen.add(key)

            results.append(
                {
                    **place,
                    "distance_m": round(
                        distance
                    ),
                }
            )

    # ========================================================
    # 2. METRO DATASET FIRST
    # ========================================================

    if category == "metro":

        metro_results = (
            _nearby_metro_from_dataset(
                lat,
                lon,
                radius,
            )
        )

        for item in metro_results:

            key = (
                round(
                    item["latitude"],
                    5,
                ),
                round(
                    item["longitude"],
                    5,
                ),
            )

            if key in seen:
                continue

            seen.add(key)
            results.append(item)

    # ========================================================
    # 3. OVERPASS
    # ========================================================

    query = _build_nearby_query(
        category,
        radius,
        lat,
        lon,
    )

    data = _overpass_request(
        query,
        timeout=14,
    )

    if data:

        processed = (
            _process_nearby_elements(
                data.get(
                    "elements",
                    []
                ),
                category,
                lat,
                lon,
                radius,
            )
        )

        for item in processed:

            key = (
                round(
                    item["latitude"],
                    5,
                ),
                round(
                    item["longitude"],
                    5,
                ),
            )

            if key in seen:
                continue

            seen.add(key)
            results.append(item)

    # ========================================================
    # 4. PHOTON FALLBACK
    # ========================================================

    # Photon is particularly useful when Overpass is down.
    if len(results) < 5:

        photon = _photon_search(
            category,
            lat,
            lon,
            radius,
        )

        for item in photon:

            key = (
                round(
                    item["latitude"],
                    5,
                ),
                round(
                    item["longitude"],
                    5,
                ),
            )

            if key in seen:
                continue

            seen.add(key)
            results.append(item)

    # ========================================================
    # 5. FINAL SORT
    # ========================================================

    results.sort(
        key=lambda item: float(
            item.get(
                "distance_m",
                10**9,
            )
        )
    )

    results = results[:40]

    print(
        f"[Nearby] Found "
        f"{len(results)} {category} "
        f"places within "
        f"{radius / 1000:.0f} km"
    )

    # IMPORTANT:
    # Return 200 even when external provider is temporarily
    # empty. This keeps frontend from showing "service unavailable"
    # for every Overpass outage.
    return JsonResponse(
        {
            "success": True,
            "results": results,
            "count": len(results),
            "radius_m": radius,
            "radius_km": radius / 1000,
            "category": category,
            "latitude": lat,
            "longitude": lon,
            "center": {
                "lat": lat,
                "lon": lon,
            },
            "scope": (
                "Delhi NCR"
                if _in_ncr(lat, lon)
                else "Current location"
            ),
            "source": (
                "GoPlan dataset + "
                "OpenStreetMap + "
                "fallback providers"
            ),
        }
    )


# ============================================================
# SMART CONNECT
# ============================================================

def smart_connect(request):

    try:

        # Existing map.js sends from_lat/from_lon/to_lat/to_lon.
        flat = float(
            request.GET.get(
                "from_lat"
            )
        )

        flon = float(
            request.GET.get(
                "from_lon"
            )
        )

        tlat = float(
            request.GET.get(
                "to_lat"
            )
        )

        tlon = float(
            request.GET.get(
                "to_lon"
            )
        )

        road_km = max(
            0.5,
            float(
                request.GET.get(
                    "distance_km",
                    "1",
                )
            ),
        )

    except (
        TypeError,
        ValueError,
    ):

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Invalid Smart Connect coordinates."
                ),
            },
            status=400,
        )

    origin_stop = _nearest_bus_stop(
        flat,
        flon,
    )

    destination_stop = _nearest_bus_stop(
        tlat,
        tlon,
    )

    pickup_km = (
        origin_stop["distance_m"] / 1000
        if origin_stop
        else 0.5
    )

    final_km = (
        destination_stop["distance_m"] / 1000
        if destination_stop
        else 0.5
    )

    bus_distance = max(
        1,
        road_km - pickup_km - final_km,
    )

    auto_fare = max(
        30,
        round(
            (30 + 12 * pickup_km) / 5
        ) * 5,
    )

    bus_fare = min(
        50,
        max(
            10,
            round(
                (10 + 1.4 * bus_distance) / 5
            ) * 5,
        ),
    )

    auto_min = max(
        3,
        round(
            pickup_km * 5
        ),
    )

    bus_min = max(
        8,
        round(
            bus_distance / 18 * 60
        ),
    )

    walk_min = max(
        2,
        round(
            final_km * 12
        ),
    )

    total_fare = (
        auto_fare
        + bus_fare
    )

    total_minutes = (
        auto_min
        + bus_min
        + walk_min
    )

    return JsonResponse(
        {
            "success": True,
            "origin_stop": (
                origin_stop or {}
            ),
            "destination_stop": (
                destination_stop or {}
            ),
            "auto_fare": auto_fare,
            "bus_fare": bus_fare,
            "total_fare": total_fare,
            "bus_text": (
                f"~{bus_distance:.1f} km "
                "estimated bus leg · "
                f"{bus_min} min"
            ),
            "total_time_text": (
                f"~{total_minutes} min"
            ),
            "note": (
                "Bus route and fare are estimates. "
                "No live bus departure is claimed."
            ),
        }
    )


# ============================================================
# WEATHER
# ============================================================

def weather(request):

    try:

        lat = float(
            request.GET["lat"]
        )

        lon = float(
            request.GET["lon"]
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):

        return JsonResponse(
            {
                "error": (
                    "Invalid coordinates"
                )
            },
            status=400,
        )

    if not (
        -90 <= lat <= 90
        and -180 <= lon <= 180
    ):

        return JsonResponse(
            {
                "error": (
                    "Invalid geographic coordinates"
                )
            },
            status=400,
        )

    params = urllib.parse.urlencode(
        {
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m,"
                "visibility"
            ),
            "daily": (
                "weather_code,"
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max,"
                "wind_speed_10m_max,"
                "sunrise,"
                "sunset"
            ),
            "forecast_days": 7,
            "timezone": "auto",
        }
    )

    try:

        data = _json_request(
            f"{WEATHER_URL}?{params}",
            timeout=10,
        )

        data["goplan"] = {
            "scope": (
                "Delhi NCR"
                if _in_ncr(
                    lat,
                    lon,
                )
                else "Current location"
            ),
            "updated_at": (
                datetime.utcnow()
                .isoformat(
                    timespec="seconds"
                )
                + "Z"
            ),
        }

        return JsonResponse(
            data
        )

    except Exception as error:

        return JsonResponse(
            {
                "error": str(error)
            },
            status=502,
        )


# ============================================================
# AWARENESS
# ============================================================

def awareness(request):

    hour = datetime.now().hour

    mode = request.GET.get(
        "mode",
        "car",
    )

    tips = []

    if hour >= 22 or hour < 6:

        tips.append(
            "Late-hour awareness: prefer "
            "well-lit, busy routes and keep "
            "your phone charged."
        )

    else:

        tips.append(
            "Stay aware at crossings and "
            "keep your route visible while moving."
        )

    mode_tips = {

        "foot": (
            "Walking tip: use pedestrian "
            "crossings and sidewalks."
        ),

        "bike": (
            "Bike tip: use a helmet and "
            "lights after dark."
        ),

        "car": (
            "Driving tip: follow local signs "
            "and don't use your phone while moving."
        ),
    }

    tips.append(
        mode_tips.get(
            mode,
            "Stay alert while travelling.",
        )
    )

    if request.GET.get(
        "rain"
    ) == "1":

        tips.append(
            "Rain-aware: allow extra travel "
            "time and watch for slippery surfaces."
        )

    return JsonResponse(
        {
            "tips": tips
        }
    )


# ============================================================
# TRAIN PLANNER
# ============================================================

def train_schedule(request):

    return JsonResponse(
        {
            "title": "Rail planning",
            "notice": (
                "These are planning windows, "
                "not live train departures."
            ),
            "slots": [
                {
                    "label": "Morning",
                    "time": "06:00–10:00",
                    "note": (
                        "Good for early departures"
                    ),
                },
                {
                    "label": "Day",
                    "time": "10:00–16:00",
                    "note": (
                        "Typical daytime planning window"
                    ),
                },
                {
                    "label": "Evening",
                    "time": "16:00–21:00",
                    "note": (
                        "Allow extra interchange time"
                    ),
                },
                {
                    "label": "Late",
                    "time": "21:00–23:00",
                    "note": (
                        "Check the operator before travelling"
                    ),
                },
            ],
        }
    )