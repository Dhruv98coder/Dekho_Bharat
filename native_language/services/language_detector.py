"""
Native Language AI - Language Detection

Uses the original Hugging Face detector:
    pruthwik/ilid-muril-model

Design:
- Roman Hindi detection remains local and fast.
- Devanagari Hindi is detected locally.
- Otherwise the original transformer detector is used.
- Model is loaded lazily.
- Model is loaded only once per Django worker.
- Hugging Face cache is reused automatically.
"""

import os
import re
import threading


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = os.getenv(
    "NATIVE_LANGUAGE_DETECTOR_MODEL",
    "pruthwik/ilid-muril-model",
)

# IMPORTANT:
# Keep the original model enabled by default.
#
# Set:
# NATIVE_AI_MODEL_ENABLED=False
#
# only when you intentionally want to disable the transformer
# detector on a low-memory deployment.
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
# MODEL STATE
# ============================================================

_classifier = None
_classifier_lock = threading.Lock()


def _get_classifier():
    """
    Lazily load the original Hugging Face classifier.

    The same classifier instance is reused inside the Django
    worker process.
    """

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

            _classifier = pipeline(
                "text-classification",
                model=MODEL_NAME,
            )

            return _classifier

        except Exception as error:

            print(
                "[NativeLanguage] "
                "Detector model loading failed:",
                repr(error),
            )

            _classifier = None

            raise RuntimeError(
                "Native Language detection model could not be loaded."
            ) from error


# ============================================================
# LANGUAGE LABEL MAP
# ============================================================

LANGUAGE_MAP = {
    "hi": "Hindi",
    "en": "English",
    "Hindi": "Hindi",
    "English": "English",

    # Keep unknown labels safe.
    "LABEL_0": "Unknown",
    "LABEL_1": "Unknown",
    "LABEL_2": "Unknown",
    "LABEL_3": "Unknown",
    "LABEL_4": "Unknown",
    "LABEL_5": "Unknown",
}


# ============================================================
# ROMAN HINDI WORDS
# ============================================================

ROMAN_HINDI_WORDS = {
    # Greetings
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

    # Pronouns
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

    # Demonstratives
    "yeh",
    "ye",
    "woh",
    "wo",
    "isko",
    "usko",
    "yahan",
    "wahan",

    # Questions
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

    # Verbs
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

    # Common
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

    # Travel
    "safar",
    "yatra",
    "paryatan",
    "tourist",
    "dekho",
    "batao",
    "dikhao",
}


# ============================================================
# STRONG ROMAN HINDI WORDS
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
# ROMAN → DEVANAGARI
# ============================================================

ROMAN_TO_DEVANAGARI = {
    "namaste": "नमस्ते",
    "namastee": "नमस्ते",
    "namaskar": "नमस्कार",
    "pranam": "प्रणाम",
    "shukriya": "शुक्रिया",
    "dhanyawad": "धन्यवाद",
    "dhanyavad": "धन्यवाद",
    "bhai": "भाई",
    "bhaiya": "भैया",
    "didi": "दीदी",
    "ji": "जी",
    "jii": "जी",

    "main": "मैं",
    "mai": "मैं",
    "mein": "में",
    "mujhe": "मुझे",
    "mujhko": "मुझको",

    "mera": "मेरा",
    "meri": "मेरी",
    "mere": "मेरे",

    "hum": "हम",
    "ham": "हम",

    "aap": "आप",
    "ap": "आप",

    "tum": "तुम",
    "tujhe": "तुझे",

    "tera": "तेरा",
    "teri": "तेरी",
    "tere": "तेरे",

    "yeh": "यह",
    "ye": "यह",

    "woh": "वह",
    "wo": "वह",

    "isko": "इसको",
    "usko": "उसको",

    "yahan": "यहाँ",
    "wahan": "वहाँ",

    "kya": "क्या",
    "kyu": "क्यों",
    "kyun": "क्यों",
    "kyon": "क्यों",

    "kaise": "कैसे",
    "kaisa": "कैसा",
    "kaisi": "कैसी",

    "kab": "कब",

    "kahan": "कहाँ",
    "kahaan": "कहाँ",

    "kaun": "कौन",

    "hai": "है",
    "hain": "हैं",
    "ho": "हो",

    "tha": "था",
    "thi": "थी",
    "the": "थे",

    "hoga": "होगा",
    "hogi": "होगी",

    "kar": "कर",
    "karo": "करो",
    "karna": "करना",
    "karta": "करता",
    "karte": "करते",
    "karti": "करती",

    "chahiye": "चाहिए",

    "chahta": "चाहता",
    "chahti": "चाहती",

    "jana": "जाना",
    "jaana": "जाना",
    "jao": "जाओ",

    "aana": "आना",
    "aao": "आओ",

    "dekhna": "देखना",
    "dekho": "देखो",

    "batao": "बताओ",
    "bata": "बता",

    "dikhao": "दिखाओ",
    "dikha": "दिखा",

    "do": "दो",
    "dena": "देना",
    "lena": "लेना",
    "lo": "लो",
    "lelo": "लेलो",
    "dijiye": "दीजिए",

    "accha": "अच्छा",
    "achha": "अच्छा",
    "acha": "अच्छा",

    "bahut": "बहुत",
    "thoda": "थोड़ा",
    "zyada": "ज़्यादा",

    "sab": "सब",
    "kuch": "कुछ",
    "koi": "कोई",

    "nahi": "नहीं",
    "nahin": "नहीं",

    "haan": "हाँ",
    "han": "हाँ",

    "aur": "और",
    "lekin": "लेकिन",
    "ya": "या",

    "se": "से",
    "ko": "को",
    "ke": "के",
    "ki": "की",
    "ka": "का",

    "par": "पर",
    "pe": "पे",

    "liye": "लिए",

    "wala": "वाला",
    "wali": "वाली",
    "wale": "वाले",

    "lagta": "लगता",
    "lagti": "लगती",

    "pasand": "पसंद",

    "jagah": "जगह",
    "jagahen": "जगहें",

    "sundar": "सुंदर",
    "khubsurat": "खूबसूरत",

    "ghoomna": "घूमना",
    "ghumna": "घूमना",
    "ghoomne": "घूमने",
    "ghumne": "घूमने",
    "ghumo": "घूमो",

    "safar": "सफ़र",
    "yatra": "यात्रा",
    "paryatan": "पर्यटन",
}


# ============================================================
# TEXT NORMALIZATION
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
# ROMAN HINDI
# ============================================================

def detect_roman_hindi(text):
    text = normalize_text(text)

    if not text:
        return {
            "is_roman_hindi": False,
            "confidence": 0.0,
        }

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
        ratio = hindi_matches / len(words)

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

    if hindi_matches >= 1 and len(words) <= 5:
        return {
            "is_roman_hindi": True,
            "confidence": 80.0,
        }

    return {
        "is_roman_hindi": False,
        "confidence": 0.0,
    }


# ============================================================
# ROMAN HINDI → DEVANAGARI
# ============================================================

def roman_hindi_to_devanagari(text):
    text = normalize_text(text)

    if not text:
        return ""

    words = text.split()
    converted_words = []

    for word in words:

        match = re.match(
            r"^([^a-zA-Z]*)([a-zA-Z]+)([^a-zA-Z]*)$",
            word,
        )

        if not match:
            converted_words.append(word)
            continue

        prefix = match.group(1)
        core = match.group(2)
        suffix = match.group(3)

        converted = ROMAN_TO_DEVANAGARI.get(
            core.lower(),
            core,
        )

        converted_words.append(
            prefix
            + converted
            + suffix
        )

    return " ".join(
        converted_words
    )


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
    # 1. Roman Hindi
    # --------------------------------------------------------

    roman_result = detect_roman_hindi(text)

    if roman_result["is_roman_hindi"]:
        return {
            "language": "Hindi",
            "language_code": "hi",
            "label": "hi",
            "confidence": roman_result["confidence"],
            "roman_hindi": True,
        }

    # --------------------------------------------------------
    # 2. Devanagari
    #
    # This preserves the original behavior of your old system.
    # --------------------------------------------------------

    if contains_devanagari(text):
        return {
            "language": "Hindi",
            "language_code": "hi",
            "label": "hi",
            "confidence": 99.0,
            "roman_hindi": False,
        }

    # --------------------------------------------------------
    # 3. Original transformer model
    #
    # English text reaches the original model instead of a
    # homemade word list.
    # --------------------------------------------------------

    try:

        classifier = _get_classifier()

        if classifier is None:
            return {
                "language": "Unknown",
                "language_code": "unknown",
                "label": "unknown",
                "confidence": 0.0,
                "roman_hindi": False,
            }

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

        if language_name == "Unknown":

            return {
                "language": "Unknown",
                "language_code": "unknown",
                "label": raw_label,
                "confidence": confidence,
                "roman_hindi": False,
            }

        language_code = {
            "Hindi": "hi",
            "English": "en",
        }.get(
            language_name,
            raw_label,
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