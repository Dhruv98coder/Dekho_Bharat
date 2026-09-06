from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import json

from native_language.services.translation import (
    translate_hindi_to_english,
    translate_english_to_hindi,
)

from native_language.services.language_detector import (
    detect_language,
    detect_roman_hindi,
    roman_hindi_to_devanagari,
)
# ============================================================
# TRANSLATION SERVICES
# ============================================================



# ============================================================
# HOME
# ============================================================

def home(request):

    return render(
        request,
        "native_language/index.html",
        {"active_module": "native"}
    )


# ============================================================
# LANGUAGE DETECTION API
# ============================================================

@csrf_exempt
def detect(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,

                "error":
                    "Only POST requests are allowed."
            },

            status=405
        )


    try:

        # ----------------------------------------------------
        # READ JSON
        # ----------------------------------------------------

        data = json.loads(
            request.body
        )


        text = data.get(
            "text",
            ""
        ).strip()


        # ----------------------------------------------------
        # EMPTY INPUT
        # ----------------------------------------------------

        if not text:

            return JsonResponse(
                {
                    "success": False,

                    "error":
                        "Please enter some text."
                },

                status=400
            )


        # ----------------------------------------------------
        # DETECT LANGUAGE
        # ----------------------------------------------------

        result = detect_language(
            text
        )


        print(
            "Detection result:",
            result
        )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return JsonResponse(
            {
                "success": True,

                **result
            }
        )


    except json.JSONDecodeError:

        return JsonResponse(
            {
                "success": False,

                "error":
                    "Invalid JSON request."
            },

            status=400
        )


    except Exception as error:

        print(
            "Detection error:",
            repr(error)
        )


        return JsonResponse(
            {
                "success": False,

                "error":
                    str(error)
            },

            status=500
        )


# ============================================================
# TRANSLATION API
# ============================================================

@csrf_exempt
def translate(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,

                "error":
                    "Only POST requests are allowed."
            },

            status=405
        )


    try:

        # ====================================================
        # READ JSON
        # ====================================================

        data = json.loads(
            request.body
        )


        text = data.get(
            "text",
            ""
        ).strip()


        # ====================================================
        # EMPTY INPUT
        # ====================================================

        if not text:

            return JsonResponse(
                {
                    "success": False,

                    "error":
                        "Please enter some text."
                },

                status=400
            )


        print(
            "\n=============================="
        )

        print(
            "INPUT:",
            text
        )


        # ====================================================
        # ROMAN HINDI DETECTION
        # ====================================================

        roman_result = detect_roman_hindi(
            text
        )


        print(
            "ROMAN HINDI:",
            roman_result
        )


        # ====================================================
        # LANGUAGE DETECTION
        # ====================================================

        language_info = detect_language(
            text
        )


        print(
            "LANGUAGE:",
            language_info
        )


        # ====================================================
        # ROMAN HINDI
        # ====================================================

        if roman_result["is_roman_hindi"]:

            normalized_text = (
                roman_hindi_to_devanagari(
                    text
                )
            )


            print(
                "NORMALIZED:",
                normalized_text
            )


            # ------------------------------------------------
            # Hindi → English
            # ------------------------------------------------

            english_text = (
                translate_hindi_to_english(
                    normalized_text
                )
            )


            print(
                "TRANSLATION:",
                english_text
            )


            print(
                "==============================\n"
            )


            return JsonResponse(
                {
                    "success": True,

                    "original_text": text,

                    "detected_language": "Hindi",

                    "language_code": "hi",

                    "roman_hindi": True,

                    "confidence":
                        roman_result["confidence"],

                    "normalized_text":
                        normalized_text,

                    "translation":
                        english_text,

                    "target_language":
                        "English",

                    "target_language_code":
                        "en"
                }
            )


        # ====================================================
        # DEVANAGARI HINDI
        # ====================================================

        if language_info["language"] == "Hindi":

            english_text = (
                translate_hindi_to_english(
                    text
                )
            )


            print(
                "TRANSLATION:",
                english_text
            )


            print(
                "==============================\n"
            )


            return JsonResponse(
                {
                    "success": True,

                    "original_text": text,

                    "detected_language": "Hindi",

                    "language_code": "hi",

                    "roman_hindi": False,

                    "confidence":
                        language_info["confidence"],

                    "translation":
                        english_text,

                    "target_language":
                        "English",

                    "target_language_code":
                        "en"
                }
            )


        # ====================================================
        # ENGLISH → HINDI
        # ====================================================

        if language_info["language"] == "English":

            print(
                "English input detected."
            )


            hindi_text = (
                translate_english_to_hindi(
                    text
                )
            )


            print(
                "English → Hindi:",
                hindi_text
            )


            print(
                "==============================\n"
            )


            return JsonResponse(
                {
                    "success": True,

                    "original_text": text,

                    "detected_language":
                        "English",

                    "language_code":
                        "en",

                    "roman_hindi":
                        False,

                    "confidence":
                        language_info["confidence"],

                    "translation":
                        hindi_text,

                    "target_language":
                        "Hindi",

                    "target_language_code":
                        "hi"
                }
            )


        # ====================================================
        # UNKNOWN / OTHER LANGUAGE
        # ====================================================

        print(
            "Other/Unknown language:",
            language_info
        )


        print(
            "==============================\n"
        )


        return JsonResponse(
            {
                "success": True,

                "original_text":
                    text,

                "detected_language":
                    language_info["language"],

                "language_code":
                    language_info["language_code"],

                "roman_hindi":
                    False,

                "confidence":
                    language_info["confidence"],

                "translation":
                    text,

                "target_language":
                    "English",

                "target_language_code":
                    "en"
            }
        )


    # ========================================================
    # INVALID JSON
    # ========================================================

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "success": False,

                "error":
                    "Invalid JSON request."
            },

            status=400
        )


    # ========================================================
    # OTHER ERRORS
    # ========================================================

    except Exception as error:

        print(
            "Translation error:",
            repr(error)
        )


        return JsonResponse(
            {
                "success": False,

                "error":
                    str(error)
            },

            status=500
        )