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

    return bool(
        re.search(
            r"[A-Za-z]",
            text,
        )
    )


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
# DETECT LANGUAGE
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
            request.body or b"{}"
        )

        text = str(
            data.get(
                "text",
                "",
            ) or ""
        ).strip()

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
        # DIRECT HINDI SCRIPT
        # ====================================================

        if contains_devanagari(text):

            return JsonResponse(
                {
                    "success": True,
                    "language": "Hindi",
                    "language_code": "hi",
                    "confidence": 1.0,
                }
            )

        # ====================================================
        # ROMAN HINDI
        # ====================================================

        try:

            roman_result = detect_roman_hindi(
                text
            )

            if (
                isinstance(
                    roman_result,
                    dict,
                )
                and roman_result.get(
                    "is_roman_hindi",
                    False,
                )
            ):

                return JsonResponse(
                    {
                        "success": True,
                        "language": "Hindi",
                        "language_code": "hi",
                        "confidence":
                            roman_result.get(
                                "confidence",
                                0.90,
                            ),
                    }
                )

        except Exception as error:

            print(
                "[NativeLanguage] "
                "Roman Hindi detection error:",
                repr(error),
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
                dict,
            ):

                return JsonResponse(
                    {
                        "success": True,
                        **result,
                    }
                )

        except Exception as error:

            print(
                "[NativeLanguage] "
                "Language detector error:",
                repr(error),
            )

        # ====================================================
        # ENGLISH FALLBACK
        # ====================================================

        if looks_like_english(text):

            return JsonResponse(
                {
                    "success": True,
                    "language": "English",
                    "language_code": "en",
                    "confidence": 0.80,
                }
            )

        # ====================================================
        # UNKNOWN
        # ====================================================

        return JsonResponse(
            {
                "success": True,
                "language": "Unknown",
                "language_code": "unknown",
                "confidence": 0.0,
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
            "Detection API error:",
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
# TRANSLATE
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

        data = json.loads(
            request.body or b"{}"
        )

        text = str(
            data.get(
                "text",
                "",
            ) or ""
        ).strip()

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
        # DEVANAGARI HINDI
        # ====================================================
        #
        # Directly send to REAL ML translator.
        #
        # ====================================================

        if contains_devanagari(text):

            print(
                "[NativeLanguage] "
                "Hindi detected from Devanagari."
            )

            translated = (
                translate_hindi_to_english(
                    text
                )
            )

            print(
                "[NativeLanguage] "
                "FINAL TRANSLATION:",
                translated,
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
                        translated,

                    "target_language":
                        "English",

                    "target_language_code":
                        "en",
                }
            )

        # ====================================================
        # ROMAN HINDI
        # ====================================================

        roman_result = {
            "is_roman_hindi": False,
            "confidence": 0.0,
        }

        try:

            detected_roman = (
                detect_roman_hindi(
                    text
                )
            )

            if isinstance(
                detected_roman,
                dict,
            ):

                roman_result = {
                    "is_roman_hindi":
                        bool(
                            detected_roman.get(
                                "is_roman_hindi",
                                False,
                            )
                        ),

                    "confidence":
                        detected_roman.get(
                            "confidence",
                            0.0,
                        ),
                }

        except Exception as error:

            print(
                "[NativeLanguage] "
                "Roman Hindi detector error:",
                repr(error),
            )

        if roman_result[
            "is_roman_hindi"
        ]:

            try:

                normalized_text = (
                    roman_hindi_to_devanagari(
                        text
                    )
                )

            except Exception as error:

                print(
                    "[NativeLanguage] "
                    "Roman Hindi conversion error:",
                    repr(error),
                )

                normalized_text = text

            if not normalized_text:

                normalized_text = text

            translated = (
                translate_hindi_to_english(
                    normalized_text
                )
            )

            print(
                "[NativeLanguage] "
                "ROMAN HINDI OUTPUT:",
                translated,
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
                        translated,

                    "target_language":
                        "English",

                    "target_language_code":
                        "en",
                }
            )

        # ====================================================
        # ENGLISH
        # ====================================================

        language_info = None

        try:

            result = detect_language(
                text
            )

            if isinstance(
                result,
                dict,
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
        # ENGLISH -> HINDI
        # ====================================================

        if (
            language_info
            and language_info.get(
                "language"
            ) == "English"
        ):

            translated = (
                translate_english_to_hindi(
                    text
                )
            )

            print(
                "[NativeLanguage] "
                "ENGLISH -> HINDI:",
                translated,
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
                        translated,

                    "target_language":
                        "Hindi",

                    "target_language_code":
                        "hi",
                }
            )

        # ====================================================
        # UNKNOWN
        # ====================================================

        if language_info is None:

            language_info = {
                "language":
                    "Unknown",

                "language_code":
                    "unknown",

                "confidence":
                    0.0,
            }

        return JsonResponse(
            {
                "success": True,

                "original_text":
                    text,

                "detected_language":
                    language_info.get(
                        "language",
                        "Unknown",
                    ),

                "language_code":
                    language_info.get(
                        "language_code",
                        "unknown",
                    ),

                "roman_hindi":
                    False,

                "confidence":
                    language_info.get(
                        "confidence",
                        0.0,
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