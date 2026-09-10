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
# HELPER: DEVANAGARI DETECTION
# ============================================================

def contains_devanagari(text):
    """
    Lightweight Hindi/script detection.

    This avoids depending entirely on the external/model-based
    detector for normal Hindi text.
    """

    if not text:
        return False

    return bool(
        re.search(
            r"[\u0900-\u097F]",
            text
        )
    )


# ============================================================
# HELPER: ENGLISH DETECTION
# ============================================================

def looks_like_english(text):
    """
    Basic fallback English detection.
    """

    if not text:
        return False

    # If Devanagari exists, it is not plain English.
    if contains_devanagari(text):
        return False

    words = re.findall(
        r"[A-Za-z]+",
        text
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
        }
    )


# ============================================================
# LANGUAGE DETECTION API
# ============================================================

@csrf_exempt
def detect(request):

    # --------------------------------------------------------
    # METHOD CHECK
    # --------------------------------------------------------

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "error":
                    "Only POST requests are allowed.",
            },
            status=405,
        )

    # --------------------------------------------------------
    # MAIN
    # --------------------------------------------------------

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
        )

        if text is None:
            text = ""

        text = str(text).strip()

        # ----------------------------------------------------
        # EMPTY INPUT
        # ----------------------------------------------------

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
        # 1. DIRECT DEVANAGARI DETECTION
        # ====================================================

        if contains_devanagari(text):

            result = {
                "language": "Hindi",
                "language_code": "hi",
                "confidence": 1.0,
            }

            print(
                "[NativeLanguage] "
                "Lightweight Hindi detection:",
                result
            )

            return JsonResponse(
                {
                    "success": True,
                    **result,
                }
            )

        # ====================================================
        # 2. TRY EXISTING DETECTOR
        # ====================================================

        try:

            result = detect_language(
                text
            )

            if not isinstance(result, dict):
                raise ValueError(
                    "Language detector returned invalid data."
                )

            language = result.get(
                "language",
                ""
            )

            language_code = result.get(
                "language_code",
                ""
            )

            confidence = result.get(
                "confidence",
                0.0
            )

            # ------------------------------------------------
            # Make sure response is complete
            # ------------------------------------------------

            if language:

                final_result = {
                    "language": language,
                    "language_code":
                        language_code,
                    "confidence":
                        confidence,
                }

                print(
                    "[NativeLanguage] "
                    "Detector result:",
                    final_result
                )

                return JsonResponse(
                    {
                        "success": True,
                        **final_result,
                    }
                )

        except Exception as detector_error:

            print(
                "[NativeLanguage] "
                "Detector failed:",
                repr(detector_error)
            )

        # ====================================================
        # 3. SIMPLE ENGLISH FALLBACK
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
        # 4. UNKNOWN
        # ====================================================

        return JsonResponse(
            {
                "success": True,
                "language": "Unknown",
                "language_code": "unknown",
                "confidence": 0.0,
            }
        )

    # --------------------------------------------------------
    # INVALID JSON
    # --------------------------------------------------------

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "success": False,
                "error":
                    "Invalid JSON request.",
            },
            status=400,
        )

    # --------------------------------------------------------
    # OTHER ERROR
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # METHOD CHECK
    # --------------------------------------------------------

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "error":
                    "Only POST requests are allowed.",
            },
            status=405,
        )

    # --------------------------------------------------------
    # MAIN
    # --------------------------------------------------------

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
        )

        if text is None:
            text = ""

        text = str(text).strip()

        # ====================================================
        # EMPTY INPUT
        # ====================================================

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
            text
        )

        # ====================================================
        # 1. DIRECT DEVANAGARI HINDI
        # ====================================================
        #
        # IMPORTANT:
        # Do this BEFORE detector call.
        #
        # This means:
        # मैं दिल्ली जा रहा हूँ
        #
        # immediately enters Hindi translation path.
        #
        # ====================================================

        if contains_devanagari(text):

            print(
                "[NativeLanguage] "
                "Direct Devanagari Hindi detected."
            )

            english_text = (
                translate_hindi_to_english(
                    text
                )
            )

            print(
                "[NativeLanguage] TRANSLATION:",
                english_text
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
                dict
            ):

                roman_result = {
                    "is_roman_hindi":
                        bool(
                            detected_roman.get(
                                "is_roman_hindi",
                                False
                            )
                        ),

                    "confidence":
                        detected_roman.get(
                            "confidence",
                            0.0
                        ),
                }

        except Exception as roman_error:

            print(
                "[NativeLanguage] "
                "Roman Hindi detector failed:",
                repr(roman_error)
            )

        print(
            "[NativeLanguage] ROMAN HINDI:",
            roman_result
        )

        # ====================================================
        # 3. ROMAN HINDI -> DEVANAGARI -> ENGLISH
        # ====================================================

        if roman_result["is_roman_hindi"]:

            try:

                normalized_text = (
                    roman_hindi_to_devanagari(
                        text
                    )
                )

                if not normalized_text:
                    normalized_text = text

            except Exception as normalize_error:

                print(
                    "[NativeLanguage] "
                    "Roman Hindi normalization failed:",
                    repr(normalize_error)
                )

                normalized_text = text

            print(
                "[NativeLanguage] NORMALIZED:",
                normalized_text
            )

            english_text = (
                translate_hindi_to_english(
                    normalized_text
                )
            )

            print(
                "[NativeLanguage] TRANSLATION:",
                english_text
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
        # 4. EXISTING LANGUAGE DETECTOR
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

        except Exception as detector_error:

            print(
                "[NativeLanguage] "
                "Language detector failed:",
                repr(detector_error)
            )

        print(
            "[NativeLanguage] LANGUAGE:",
            language_info
        )

        # ====================================================
        # 5. ENGLISH FALLBACK
        # ====================================================

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
        # 6. ENGLISH -> HINDI
        # ====================================================

        if (
            language_info
            and language_info.get(
                "language"
            ) == "English"
        ):

            print(
                "[NativeLanguage] "
                "English input detected."
            )

            hindi_text = (
                translate_english_to_hindi(
                    text
                )
            )

            print(
                "[NativeLanguage] "
                "English -> Hindi:",
                hindi_text
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
                            0.80
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
        # 7. UNKNOWN / OTHER LANGUAGE
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

        detected_language = (
            language_info.get(
                "language",
                "Unknown"
            )
        )

        detected_code = (
            language_info.get(
                "language_code",
                "unknown"
            )
        )

        confidence = (
            language_info.get(
                "confidence",
                0.0
            )
        )

        print(
            "[NativeLanguage] "
            "Other/Unknown:",
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
                    detected_language,

                "language_code":
                    detected_code,

                "roman_hindi":
                    False,

                "confidence":
                    confidence,

                "translation":
                    text,

                "target_language":
                    "English",

                "target_language_code":
                    "en",
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
                    "Invalid JSON request.",
            },
            status=400,
        )

    # ========================================================
    # OTHER ERRORS
    # ========================================================

    except Exception as error:

        print(
            "[NativeLanguage] "
            "Translation error:",
            repr(error)
        )

        return JsonResponse(
            {
                "success": False,
                "error":
                    str(error),
            },
            status=500,
        )