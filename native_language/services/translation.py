"""
Native Language AI - Translation Service

PRIMARY:
    Hugging Face MarianMT model

Hindi -> English:
    Helsinki-NLP/opus-mt-hi-en

English -> Hindi:
    Helsinki-NLP/opus-mt-en-hi

Design:
    1. Real ML model is the PRIMARY translator.
    2. Models are loaded lazily.
    3. Model loading happens only when translation is requested.
    4. Models are cached per Django worker.
    5. Lightweight fallback is used ONLY when the model cannot load/fails.
    6. Model is ENABLED by default.
"""

import os
import re
import threading


# ============================================================
# MODEL CONFIGURATION
# ============================================================

HI_EN_MODEL = os.getenv(
    "NATIVE_HI_EN_MODEL",
    "Helsinki-NLP/opus-mt-hi-en",
)

EN_HI_MODEL = os.getenv(
    "NATIVE_EN_HI_MODEL",
    "Helsinki-NLP/opus-mt-en-hi",
)


# ============================================================
# MODEL ENABLE SWITCH
# ============================================================
#
# IMPORTANT:
# Model is TRUE by default.
#
# Render:
#     NATIVE_TRANSLATION_MODEL_ENABLED=True
#
# Local:
#     NATIVE_TRANSLATION_MODEL_ENABLED=True
#
# ============================================================

NATIVE_TRANSLATION_MODEL_ENABLED = (
    os.getenv(
        "NATIVE_TRANSLATION_MODEL_ENABLED",
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

_hi_en_tokenizer = None
_hi_en_model = None

_en_hi_tokenizer = None
_en_hi_model = None

_hi_en_loading = False
_en_hi_loading = False

_hi_en_failed = False
_en_hi_failed = False

_hi_en_lock = threading.Lock()
_en_hi_lock = threading.Lock()


# ============================================================
# HINDI PLACE NAMES
# ============================================================

HINDI_PLACE_NAMES = {
    "दिल्ली": "Delhi",

    "कुतुब मीनार": "Qutub Minar",
    "कुतुबमीनार": "Qutub Minar",

    "लाल किला": "Red Fort",
    "लालकिला": "Red Fort",

    "इंडिया गेट": "India Gate",
    "इंडियागेट": "India Gate",

    "हुमायूं का मकबरा": "Humayun's Tomb",

    "कमल मंदिर": "Lotus Temple",

    "जामा मस्जिद": "Jama Masjid",

    "अक्षरधाम मंदिर": "Akshardham Temple",
    "अक्षरधाम": "Akshardham Temple",

    "जंतर मंतर": "Jantar Mantar",

    "पुराना किला": "Purana Qila",

    "लोधी गार्डन": "Lodhi Garden",

    "राष्ट्रपति भवन": "Rashtrapati Bhavan",

    "राजघाट": "Raj Ghat",
}


# ============================================================
# ENGLISH PLACE NAME CORRECTIONS
# ============================================================

ENGLISH_PLACE_CORRECTIONS = {
    "QUTUB_MAR": "Qutub Minar",
    "QUTUB_MINAR": "Qutub Minar",
    "Qutub Mar": "Qutub Minar",
    "Qutub Minar": "Qutub Minar",
    "Qutb Minar": "Qutub Minar",
    "Kutub Minar": "Qutub Minar",
    "Kutub Tower": "Qutub Minar",
    "Qutub Tower": "Qutub Minar",
    "Kutble Tower": "Qutub Minar",
    "Kuthble Tower": "Qutub Minar",

    "RED_FORT": "Red Fort",
    "PALCHOLDER0": "Red Fort",
    "PALHOLDER0": "Red Fort",
    "PALCHOLDER": "Red Fort",
    "Red Kila": "Red Fort",
    "Lal Kila": "Red Fort",
    "Lal Qila": "Red Fort",

    "India Gate": "India Gate",

    "Humayun Tomb": "Humayun's Tomb",
    "Humayun's Tomb": "Humayun's Tomb",

    "Lotus Temple": "Lotus Temple",

    "Jama Mosque": "Jama Masjid",
    "Jama Masjid": "Jama Masjid",

    "Akshardham": "Akshardham Temple",
    "Akshardham Temple": "Akshardham Temple",

    "Jantar Mantar": "Jantar Mantar",

    "Old Fort": "Purana Qila",
    "Purana Qila": "Purana Qila",

    "Lodi Garden": "Lodhi Garden",
    "Lodhi Garden": "Lodhi Garden",

    "Rashtrapati Bhavan": "Rashtrapati Bhavan",
    "Raj Ghat": "Raj Ghat",
}


# ============================================================
# SAFE COMMON FALLBACK
# ============================================================
#
# IMPORTANT:
# These are NOT the main translator.
#
# They are only used if the ML model cannot be loaded.
#
# ============================================================

COMMON_HINDI_FALLBACKS = {
    "नमस्ते": "Hello.",
    "धन्यवाद": "Thank you.",
    "शुक्रिया": "Thank you.",

    "मैं दिल्ली जा रहा हूँ":
        "I am going to Delhi.",

    "मैं दिल्ली जा रहा हूं":
        "I am going to Delhi.",

    "मैं दिल्ली जा रही हूँ":
        "I am going to Delhi.",

    "मैं दिल्ली जा रही हूं":
        "I am going to Delhi.",
}


COMMON_ENGLISH_FALLBACKS = {
    "hello": "नमस्ते।",
    "hi": "नमस्ते।",
    "thank you": "धन्यवाद।",

    "i am going to delhi":
        "मैं दिल्ली जा रहा हूँ।",

    "i want to go to delhi":
        "मैं दिल्ली जाना चाहता हूँ।",
}


# ============================================================
# NORMALIZE TEXT
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
# CORRECT ENGLISH PLACE NAMES
# ============================================================

def correct_english_place_names(text):

    if not text:
        return text

    corrections = sorted(
        ENGLISH_PLACE_CORRECTIONS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for wrong, correct in corrections:

        text = re.sub(
            re.escape(wrong),
            correct,
            text,
            flags=re.IGNORECASE,
        )

    return text.strip()


# ============================================================
# HINDI PLACE REPLACEMENT
# ============================================================

def replace_hindi_place_names(text):

    if not text:
        return text

    result = text

    places = sorted(
        HINDI_PLACE_NAMES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for hindi_place, english_place in places:

        result = result.replace(
            hindi_place,
            english_place,
        )

    return result


# ============================================================
# GET HINDI -> ENGLISH MODEL
# ============================================================

def _get_hi_en():

    global _hi_en_tokenizer
    global _hi_en_model
    global _hi_en_loading
    global _hi_en_failed

    if (
        _hi_en_tokenizer is not None
        and _hi_en_model is not None
    ):
        return (
            _hi_en_tokenizer,
            _hi_en_model,
        )

    if not NATIVE_TRANSLATION_MODEL_ENABLED:

        print(
            "[NativeLanguage] "
            "Hindi->English model disabled."
        )

        return None, None

    if _hi_en_failed:

        print(
            "[NativeLanguage] "
            "Hindi->English model previously failed."
        )

        return None, None

    with _hi_en_lock:

        if (
            _hi_en_tokenizer is not None
            and _hi_en_model is not None
        ):
            return (
                _hi_en_tokenizer,
                _hi_en_model,
            )

        if _hi_en_loading:
            return None, None

        _hi_en_loading = True

        try:

            print(
                "[NativeLanguage] "
                "Loading Hindi -> English model:"
            )

            print(
                HI_EN_MODEL
            )

            from transformers import (
                AutoTokenizer,
                AutoModelForSeq2SeqLM,
            )

            tokenizer = (
                AutoTokenizer.from_pretrained(
                    HI_EN_MODEL,
                    local_files_only=False,
                )
            )

            model = (
                AutoModelForSeq2SeqLM.from_pretrained(
                    HI_EN_MODEL,
                    local_files_only=False,
                )
            )

            model.eval()

            _hi_en_tokenizer = tokenizer
            _hi_en_model = model

            print(
                "[NativeLanguage] "
                "Hindi -> English MODEL LOADED."
            )

            return (
                _hi_en_tokenizer,
                _hi_en_model,
            )

        except Exception as error:

            _hi_en_failed = True

            print(
                "[NativeLanguage] "
                "Hindi -> English MODEL LOAD ERROR:"
            )

            print(
                repr(error)
            )

            return None, None

        finally:

            _hi_en_loading = False


# ============================================================
# GET ENGLISH -> HINDI MODEL
# ============================================================

def _get_en_hi():

    global _en_hi_tokenizer
    global _en_hi_model
    global _en_hi_loading
    global _en_hi_failed

    if (
        _en_hi_tokenizer is not None
        and _en_hi_model is not None
    ):
        return (
            _en_hi_tokenizer,
            _en_hi_model,
        )

    if not NATIVE_TRANSLATION_MODEL_ENABLED:

        print(
            "[NativeLanguage] "
            "English->Hindi model disabled."
        )

        return None, None

    if _en_hi_failed:

        print(
            "[NativeLanguage] "
            "English->Hindi model previously failed."
        )

        return None, None

    with _en_hi_lock:

        if (
            _en_hi_tokenizer is not None
            and _en_hi_model is not None
        ):
            return (
                _en_hi_tokenizer,
                _en_hi_model,
            )

        if _en_hi_loading:
            return None, None

        _en_hi_loading = True

        try:

            print(
                "[NativeLanguage] "
                "Loading English -> Hindi model:"
            )

            print(
                EN_HI_MODEL
            )

            from transformers import (
                AutoTokenizer,
                AutoModelForSeq2SeqLM,
            )

            tokenizer = (
                AutoTokenizer.from_pretrained(
                    EN_HI_MODEL,
                    local_files_only=False,
                )
            )

            model = (
                AutoModelForSeq2SeqLM.from_pretrained(
                    EN_HI_MODEL,
                    local_files_only=False,
                )
            )

            model.eval()

            _en_hi_tokenizer = tokenizer
            _en_hi_model = model

            print(
                "[NativeLanguage] "
                "English -> Hindi MODEL LOADED."
            )

            return (
                _en_hi_tokenizer,
                _en_hi_model,
            )

        except Exception as error:

            _en_hi_failed = True

            print(
                "[NativeLanguage] "
                "English -> Hindi MODEL LOAD ERROR:"
            )

            print(
                repr(error)
            )

            return None, None

        finally:

            _en_hi_loading = False


# ============================================================
# ML TRANSLATION: HINDI -> ENGLISH
# ============================================================

def _model_translate_hindi_to_english(text):

    tokenizer, model = _get_hi_en()

    if tokenizer is None or model is None:

        return None

    try:

        import torch

        print(
            "[NativeLanguage] "
            "Running REAL Hindi -> English model..."
        )

        # IMPORTANT:
        # Do NOT replace Hindi place names before model inference.
        # Give the actual Hindi sentence to the model.

        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128,
        )

        with torch.no_grad():

            generated = model.generate(
                **inputs,
                max_length=128,
                num_beams=5,
                do_sample=False,
            )

        translated = tokenizer.decode(
            generated[0],
            skip_special_tokens=True,
        )

        translated = correct_english_place_names(
            translated
        )

        translated = translated.strip()

        if not translated:

            return None

        print(
            "[NativeLanguage] "
            "MODEL OUTPUT:",
            translated
        )

        return translated

    except Exception as error:

        print(
            "[NativeLanguage] "
            "Hindi -> English MODEL INFERENCE ERROR:"
        )

        print(
            repr(error)
        )

        return None


# ============================================================
# ML TRANSLATION: ENGLISH -> HINDI
# ============================================================

def _model_translate_english_to_hindi(text):

    tokenizer, model = _get_en_hi()

    if tokenizer is None or model is None:

        return None

    try:

        import torch

        print(
            "[NativeLanguage] "
            "Running REAL English -> Hindi model..."
        )

        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128,
        )

        with torch.no_grad():

            generated = model.generate(
                **inputs,
                max_length=128,
                num_beams=5,
                do_sample=False,
            )

        translated = tokenizer.decode(
            generated[0],
            skip_special_tokens=True,
        )

        translated = translated.strip()

        if not translated:

            return None

        print(
            "[NativeLanguage] "
            "MODEL OUTPUT:",
            translated
        )

        return translated

    except Exception as error:

        print(
            "[NativeLanguage] "
            "English -> Hindi MODEL INFERENCE ERROR:"
        )

        print(
            repr(error)
        )

        return None


# ============================================================
# HINDI -> ENGLISH PUBLIC FUNCTION
# ============================================================

def translate_hindi_to_english(text):

    if not text or not str(text).strip():

        return ""

    text = normalize_text(
        text
    )

    print(
        "[NativeLanguage] "
        "Hindi -> English request:",
        text
    )

    # ========================================================
    # FIRST: REAL MODEL
    # ========================================================

    model_translation = (
        _model_translate_hindi_to_english(
            text
        )
    )

    if model_translation:

        return model_translation

    # ========================================================
    # SECOND: SAFE FALLBACK
    # ========================================================

    normalized = normalize_text(
        text
    )

    if normalized in COMMON_HINDI_FALLBACKS:

        print(
            "[NativeLanguage] "
            "Using fallback because ML model failed."
        )

        return COMMON_HINDI_FALLBACKS[
            normalized
        ]

    # ========================================================
    # PLACE-NAME FALLBACK
    # ========================================================

    replaced = replace_hindi_place_names(
        text
    )

    if replaced != text:

        return replaced

    # ========================================================
    # LAST RESORT
    # ========================================================

    return text


# ============================================================
# ENGLISH -> HINDI PUBLIC FUNCTION
# ============================================================

def translate_english_to_hindi(text):

    if not text or not str(text).strip():

        return ""

    text = normalize_text(
        text
    )

    print(
        "[NativeLanguage] "
        "English -> Hindi request:",
        text
    )

    # ========================================================
    # FIRST: REAL MODEL
    # ========================================================

    model_translation = (
        _model_translate_english_to_hindi(
            text
        )
    )

    if model_translation:

        return model_translation

    # ========================================================
    # SECOND: SAFE FALLBACK
    # ========================================================

    normalized = (
        normalize_text(text)
        .lower()
    )

    if normalized in COMMON_ENGLISH_FALLBACKS:

        print(
            "[NativeLanguage] "
            "Using fallback because ML model failed."
        )

        return COMMON_ENGLISH_FALLBACKS[
            normalized
        ]

    return text


# ============================================================
# AUTO TRANSLATION
# ============================================================

def auto_translate(
    text,
    detected_language,
):

    if not text or not str(text).strip():

        return ""

    if detected_language == "Hindi":

        return translate_hindi_to_english(
            text
        )

    if detected_language == "English":

        return translate_english_to_hindi(
            text
        )

    return text