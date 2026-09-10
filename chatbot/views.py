import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .engine import (
    chat,
    get_all_places,
    get_place_by_name,
)


# =========================================================
# CHAT PAGE
# =========================================================

def chat_page(request):

    return render(
        request,
        "chatbot/chat.html",
        {"active_module": "shristi"}
    )


# =========================================================
# CHATBOT API
# =========================================================

@csrf_exempt
def chatbot_api(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "error": "Only POST requests are allowed."
            },
            status=405
        )

    try:

        body = json.loads(request.body)

        question = str(
            body.get(
                "question",
                ""
            )
        ).strip()

        if not question:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Question is required."
                },
                status=400
            )

        result = chat(question)

        return JsonResponse(
            {
                "success": True,

                "question": result.get(
                    "question",
                    question
                ),

                "intent": result.get(
                    "intent",
                    ""
                ),

                "confidence": result.get(
                    "confidence",
                    0
                ),

                "matched_words": result.get(
                    "matched_words",
                    []
                ),

                "place": result.get(
                    "place"
                ),

                "answer": result.get(
                    "answer",
                    ""
                ),

                "place_data": result.get(
                    "place_data"
                )
            }
        )

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "success": False,
                "error": "Invalid JSON request."
            },
            status=400
        )

    except Exception as e:

        print(
            "CHATBOT API ERROR:",
            repr(e)
        )

        return JsonResponse(
            {
                "success": False,
                "error": str(e)
            },
            status=500
        )


# =========================================================
# ALL PLACES API
# =========================================================

def places_api(request):

    if request.method != "GET":

        return JsonResponse(
            {
                "success": False,
                "error": "Only GET requests are allowed."
            },
            status=405
        )

    try:

        places = get_all_places()

        return JsonResponse(
            {
                "success": True,
                "count": len(places),
                "places": places
            }
        )

    except Exception as e:

        print(
            "PLACES API ERROR:",
            repr(e)
        )

        return JsonResponse(
            {
                "success": False,
                "error": str(e)
            },
            status=500
        )


# =========================================================
# SINGLE PLACE API
# =========================================================

def place_detail_api(request, place_name):

    if request.method != "GET":

        return JsonResponse(
            {
                "success": False,
                "error": "Only GET requests are allowed."
            },
            status=405
        )

    try:

        place = get_place_by_name(
            place_name
        )

        if place is None:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Place not found.",
                    "place": None
                },
                status=404
            )

        return JsonResponse(
            {
                "success": True,
                "place": place
            }
        )

    except Exception as e:

        print(
            "PLACE DETAIL API ERROR:",
            repr(e)
        )

        return JsonResponse(
            {
                "success": False,
                "error": str(e)
            },
            status=500
        )