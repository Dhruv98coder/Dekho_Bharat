"""
Native Language AI - Language Detection

Original detector:
    pruthwik/ilid-muril-model

Design:
- Roman Hindi detection remains local.
- Devanagari Hindi detection remains local.
- Transformer detector remains available.
- Model loads lazily.
- Model instance is reused within the Django worker.
"""

import os
import re
import threading


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = os.getenv(
    "NATIVE_LANGUAGE_DETECTOR_MODEL",
    "pruthwik/ilid-muril-model",
)


# ============================================================
# MODEL ENABLE
# ============================================================

NATIVE_AI_MODEL_ENABLED = (
    os.getenv(
        "NATIVE_AI_MODEL_ENABLED",
        "True",
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)


# ============================================================
# MODEL CACHE
# ============================================================

_classifier = None
_classifier_lock = threading.Lock()


def _get_classifier():

    global _classifier

    if _classifier is not None:
        return _classifier

    if not NATIVE_AI_MODEL_ENABLED:
        return None

    with _classifier_lock:

        if _classifier is not None:
            return _classifier

        try:

            from transformers import pipeline

            print(
                "[NativeLanguage] "
                "Loading language detector..."
            )

            _classifier = pipeline(
                "text-classification",
                model=MODEL_NAME,
            )

            print(
                "[NativeLanguage] "
                "Language detector loaded."
            )

            return _classifier

        except Exception as error:

            print(
                "[NativeLanguage] "
                "Language detector load error:",
                repr(error),
            )

            _classifier = None

            return None


# ============================================================
# LANGUAGE MAP
# ============================================================

LANGUAGE_MAP = {

    "hi":
        "Hindi",

    "en":
        "English",

    "Hindi":
        "Hindi",

    "English":
        "English",

    "LABEL_0":
        "Unknown",

    "LABEL_1":
        "Unknown",

    "LABEL_2":
        "Unknown",

    "LABEL_3":
        "Unknown",

    "LABEL_4":
        "Unknown",

    "LABEL_5":
        "Unknown",
}


# ============================================================
# ROMAN HINDI
# ============================================================

ROMAN_HINDI_WORDS = {
    "namaste",
    "namastee",
    "namaskar",
    "pranam",
    "shukriya",
    "dhanyawad",
    "dhanyavad",

    "bhai",
    "bhaiya",
    "didi",
    "ji",
    "jii",

    "main",
    "mai",
    "mein",
    "mujhe",
    "mujhko",
    "mera",
    "meri",
    "mere",

    "hum",
    "ham",

    "aap",
    "ap",
    "tum",
    "tujhe",

    "tera",
    "teri",
    "tere",

    "yeh",
    "ye",
    "woh",
    "wo",
    "isko",
    "usko",
    "yahan",
    "wahan",

    "kya",
    "kyu",
    "kyun",
    "kyon",
    "kaise",
    "kaisa",
    "kaisi",
    "kab",
    "kahan",
    "kahaan",
    "kaun",

    "hai",
    "hain",
    "ho",
    "tha",
    "thi",
    "the",
    "hoga",
    "hogi",

    "kar",
    "karo",
    "karna",
    "karta",
    "karte",
    "karti",

    "chahiye",
    "chahta",
    "chahti",

    "jana",
    "jaana",
    "jao",

    "aana",
    "aao",

    "dekhna",
    "dekho",

    "batao",
    "bata",

    "dikhao",
    "dikha",

    "lo",
    "do",
    "dena",
    "lena",
    "lelo",
    "dijiye",

    "accha",
    "achha",
    "acha",
    "bahut",
    "thoda",
    "zyada",

    "sab",
    "kuch",
    "koi",

    "nahi",
    "nahin",

    "haan",
    "han",

    "aur",
    "lekin",
    "ya",

    "se",
    "ko",
    "ke",
    "ki",
    "ka",

    "par",
    "pe",
    "liye",

    "wala",
    "wali",
    "wale",

    "lagta",
    "lagti",

    "pasand",
    "khubsurat",
    "sundar",

    "jagah",
    "jagahen",

    "ghoomna",
    "ghumna",
    "ghoomne",
    "ghumne",
    "ghumo",

    "travel",
    "safar",
    "yatra",
    "paryatan",
    "tourist",
    "dekho",
}


# ============================================================
# STRONG ROMAN HINDI
# ============================================================

STRONG_ROMAN_HINDI_WORDS = {
    "namaste",
    "namastee",
    "namaskar",
    "pranam",
    "shukriya",
    "dhanyawad",
    "dhanyavad",

    "bhai",
    "bhaiya",
    "didi",
    "jii",

    "mujhe",
    "mujhko",

    "mera",
    "meri",

    "main",
    "mein",

    "aap",
    "tum",

    "kya",
    "kaise",
    "kahan",
    "kyun",

    "nahi",
    "nahin",

    "haan",

    "hai",
    "hain",

    "chahiye",
}


# ============================================================
# NORMALIZE
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


# ============================================================
# DEVANAGARI
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


# ============================================================
# ROMAN HINDI DETECTION
# ============================================================

def detect_roman_hindi(text):

    text = normalize_text(text)

    if not text:
        return {
            "is_roman_hindi": False,
            "confidence": 0.0,
        }

    # Mixed Devanagari + Roman is not pure Roman Hindi.
    if contains_devanagari(text):
        return {
            "is_roman_hindi": False,
            "confidence": 0.0,
        }

    words = re.findall(
        r"[a-zA-Z]+",
        text.lower(),
    )

    if not words:
        return {
            "is_roman_hindi": False,
            "confidence": 0.0,
        }

    hindi_matches = sum(
        1
        for word in words
        if word in ROMAN_HINDI_WORDS
    )

    strong_matches = sum(
        1
        for word in words
        if word in STRONG_ROMAN_HINDI_WORDS
    )

    if strong_matches >= 1:
        return {
            "is_roman_hindi": True,
            "confidence": 90.0,
        }

    if hindi_matches >= 2:

        ratio = (
            hindi_matches
            / len(words)
        )

        confidence = min(
            98.0,
            70.0 + ratio * 28.0,
        )

        return {
            "is_roman_hindi": True,
            "confidence": round(
                confidence,
                2,
            ),
        }

    if (
        hindi_matches >= 1
        and len(words) <= 5
    ):
        return {
            "is_roman_hindi": True,
            "confidence": 80.0,
        }

    return {
        "is_roman_hindi": False,
        "confidence": 0.0,
    }


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text):

    text = normalize_text(text)

    if not text:
        return {
            "language": "Unknown",
            "language_code": "unknown",
            "label": "unknown",
            "confidence": 0.0,
            "roman_hindi": False,
        }

    # --------------------------------------------------------
    # Roman Hindi
    # --------------------------------------------------------

    roman_result = (
        detect_roman_hindi(text)
    )

    if roman_result["is_roman_hindi"]:

        return {
            "language": "Hindi",
            "language_code": "hi",
            "label": "hi",
            "confidence": roman_result["confidence"],
            "roman_hindi": True,
        }

    # --------------------------------------------------------
    # Pure Devanagari
    # --------------------------------------------------------

    if contains_devanagari(text):

        # If there is also a meaningful amount of Latin text,
        # send mixed-language text to the original detector.
        latin_words = re.findall(
            r"[a-zA-Z]+",
            text,
        )

        devanagari_chars = re.findall(
            r"[\u0900-\u097F]",
            text,
        )

        if (
            len(latin_words) == 0
            or len(devanagari_chars)
            >= len(latin_words) * 3
        ):

            return {
                "language": "Hindi",
                "language_code": "hi",
                "label": "hi",
                "confidence": 99.0,
                "roman_hindi": False,
            }

    # --------------------------------------------------------
    # Original transformer model
    # --------------------------------------------------------

    classifier = _get_classifier()

    if classifier is None:

        return {
            "language": "Unknown",
            "language_code": "unknown",
            "label": "unknown",
            "confidence": 0.0,
            "roman_hindi": False,
        }

    try:

        result = classifier(text)

        if not result:

            return {
                "language": "Unknown",
                "language_code": "unknown",
                "label": "unknown",
                "confidence": 0.0,
                "roman_hindi": False,
            }

        result = result[0]

        raw_label = str(
            result.get(
                "label",
                "unknown",
            )
        )

        confidence = round(
            float(
                result.get(
                    "score",
                    0.0,
                )
            ) * 100,
            2,
        )

        language_name = LANGUAGE_MAP.get(
            raw_label,
            "Unknown",
        )

        language_code = {
            "Hindi": "hi",
            "English": "en",
        }.get(
            language_name,
            "unknown",
        )

        return {
            "language": language_name,
            "language_code": language_code,
            "label": raw_label,
            "confidence": confidence,
            "roman_hindi": False,
        }

    except Exception as error:

        print(
            "[NativeLanguage] "
            "Detection error:",
            repr(error),
        )

        return {
            "language": "Unknown",
            "language_code": "unknown",
            "label": "unknown",
            "confidence": 0.0,
            "roman_hindi": False,
        }