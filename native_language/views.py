from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import json
import re

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
# HELPERS
# ============================================================

def contains_devanagari(text):

    if not text:
        return False

    return bool(
        re.search(
            r"[\u0900-\u097F]",
            text,
        )
    )


def looks_like_english(text):

    if not text:
        return False

    if contains_devanagari(text):
        return False

    words = re.findall(
        r"[A-Za-z]+",
        text,
    )

    return len(words) > 0


# ============================================================
# HOME
# ============================================================

def home(request):

    return render(
        request,
        "native_language/index.html",
        {
            "active_module": "native"
        },
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
                    "Only POST requests are allowed.",
            },
            status=405,
        )

    try:

        data = json.loads(
            request.body
        )

        text = data.get(
            "text",
            "",
        )

        if text is None:
            text = ""

        text = str(text).strip()

        if not text:

            return JsonResponse(
                {
                    "success": False,
                    "error":
                        "Please enter some text.",
                },
                status=400,
            )

        # ====================================================
        # DIRECT HINDI SCRIPT DETECTION
        # ====================================================

        if contains_devanagari(text):

            result = {
                "language":
                    "Hindi",

                "language_code":
                    "hi",

                "confidence":
                    1.0,
            }

            print(
                "[NativeLanguage] "
                "Hindi detected directly:",
                result,
            )

            return JsonResponse(
                {
                    "success": True,
                    **result,
                }
            )

        # ====================================================
        # EXISTING DETECTOR
        # ====================================================

        try:

            result = detect_language(
                text
            )

            if isinstance(
                result,
                dict
            ):

                return JsonResponse(
                    {
                        "success": True,
                        **result,
                    }
                )

        except Exception as detector_error:

            print(
                "[NativeLanguage] "
                "Detector error:",
                repr(detector_error),
            )

        # ====================================================
        # ENGLISH FALLBACK
        # ====================================================

        if looks_like_english(text):

            return JsonResponse(
                {
                    "success": True,

                    "language":
                        "English",

                    "language_code":
                        "en",

                    "confidence":
                        0.80,
                }
            )

        # ====================================================
        # UNKNOWN
        # ====================================================

        return JsonResponse(
            {
                "success": True,

                "language":
                    "Unknown",

                "language_code":
                    "unknown",

                "confidence":
                    0.0,
            }
        )

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "success": False,
                "error":
                    "Invalid JSON request.",
            },
            status=400,
        )

    except Exception as error:

        print(
            "[NativeLanguage] "
            "Detection error:",
            repr(error),
        )

        return JsonResponse(
            {
                "success": False,
                "error":
                    str(error),
            },
            status=500,
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
                    "Only POST requests are allowed.",
            },
            status=405,
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
            "",
        )

        if text is None:
            text = ""

        text = str(text).strip()

        if not text:

            return JsonResponse(
                {
                    "success": False,
                    "error":
                        "Please enter some text.",
                },
                status=400,
            )

        print(
            "\n=============================="
        )

        print(
            "[NativeLanguage] INPUT:",
            text,
        )

        # ====================================================
        # 1. DEVANAGARI HINDI
        # ====================================================
        #
        # Do this BEFORE language detector.
        #
        # Example:
        #     मैं खाना खाने जा रहा हूँ
        #
        # This goes directly to REAL ML translation.
        #
        # ====================================================

        if contains_devanagari(text):

            print(
                "[NativeLanguage] "
                "Devanagari Hindi detected."
            )

            english_text = (
                translate_hindi_to_english(
                    text
                )
            )

            print(
                "[NativeLanguage] "
                "FINAL TRANSLATION:",
                english_text,
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
                        "Hindi",

                    "language_code":
                        "hi",

                    "roman_hindi":
                        False,

                    "confidence":
                        1.0,

                    "translation":
                        english_text,

                    "target_language":
                        "English",

                    "target_language_code":
                        "en",
                }
            )

        # ====================================================
        # 2. ROMAN HINDI
        # ====================================================

        roman_result = {
            "is_roman_hindi":
                False,

            "confidence":
                0.0,
        }

        try:

            result = detect_roman_hindi(
                text
            )

            if isinstance(
                result,
                dict
            ):

                roman_result = {
                    "is_roman_hindi":
                        bool(
                            result.get(
                                "is_roman_hindi",
                                False,
                            )
                        ),

                    "confidence":
                        result.get(
                            "confidence",
                            0.0,
                        ),
                }

        except Exception as roman_error:

            print(
                "[NativeLanguage] "
                "Roman Hindi detection error:",
                repr(roman_error),
            )

        # ====================================================
        # 3. ROMAN HINDI
        # ====================================================

        if roman_result["is_roman_hindi"]:

            try:

                normalized_text = (
                    roman_hindi_to_devanagari(
                        text
                    )
                )

            except Exception as error:

                print(
                    "[NativeLanguage] "
                    "Roman Hindi normalization error:",
                    repr(error),
                )

                normalized_text = text

            if not normalized_text:

                normalized_text = text

            print(
                "[NativeLanguage] "
                "Roman Hindi normalized:",
                normalized_text,
            )

            english_text = (
                translate_hindi_to_english(
                    normalized_text
                )
            )

            print(
                "[NativeLanguage] "
                "FINAL TRANSLATION:",
                english_text,
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
                        "Hindi",

                    "language_code":
                        "hi",

                    "roman_hindi":
                        True,

                    "confidence":
                        roman_result[
                            "confidence"
                        ],

                    "normalized_text":
                        normalized_text,

                    "translation":
                        english_text,

                    "target_language":
                        "English",

                    "target_language_code":
                        "en",
                }
            )

        # ====================================================
        # 4. ENGLISH
        # ====================================================

        language_info = None

        try:

            result = detect_language(
                text
            )

            if isinstance(
                result,
                dict
            ):

                language_info = result

        except Exception as error:

            print(
                "[NativeLanguage] "
                "Language detector error:",
                repr(error),
            )

        if (
            language_info is None
            and looks_like_english(text)
        ):

            language_info = {
                "language":
                    "English",

                "language_code":
                    "en",

                "confidence":
                    0.80,
            }

        # ====================================================
        # 5. ENGLISH -> HINDI
        # ====================================================

        if (
            language_info
            and language_info.get(
                "language"
            ) == "English"
        ):

            hindi_text = (
                translate_english_to_hindi(
                    text
                )
            )

            print(
                "[NativeLanguage] "
                "FINAL ENGLISH -> HINDI:",
                hindi_text,
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
                        "English",

                    "language_code":
                        "en",

                    "roman_hindi":
                        False,

                    "confidence":
                        language_info.get(
                            "confidence",
                            0.80,
                        ),

                    "translation":
                        hindi_text,

                    "target_language":
                        "Hindi",

                    "target_language_code":
                        "hi",
                }
            )

        # ====================================================
        # 6. UNKNOWN
        # ====================================================

        return JsonResponse(
            {
                "success": True,

                "original_text":
                    text,

                "detected_language":
                    (
                        language_info.get(
                            "language",
                            "Unknown",
                        )
                        if language_info
                        else "Unknown"
                    ),

                "language_code":
                    (
                        language_info.get(
                            "language_code",
                            "unknown",
                        )
                        if language_info
                        else "unknown"
                    ),

                "roman_hindi":
                    False,

                "confidence":
                    (
                        language_info.get(
                            "confidence",
                            0.0,
                        )
                        if language_info
                        else 0.0
                    ),

                "translation":
                    text,

                "target_language":
                    "English",

                "target_language_code":
                    "en",
            }
        )

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "success": False,
                "error":
                    "Invalid JSON request.",
            },
            status=400,
        )

    except Exception as error:

        print(
            "[NativeLanguage] "
            "TRANSLATION API ERROR:",
            repr(error),
        )

        return JsonResponse(
            {
                "success": False,
                "error":
                    str(error),
            },
            status=500,
        )