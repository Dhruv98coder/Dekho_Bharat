import os
import re
import threading

HI_EN_MODEL = os.getenv(
    "NATIVE_HI_EN_MODEL",
    "Helsinki-NLP/opus-mt-hi-en",
)

EN_HI_MODEL = os.getenv(
    "NATIVE_EN_HI_MODEL",
    "Helsinki-NLP/opus-mt-en-hi",
)

# ============================================================
# REAL ML MODEL IS ENABLED BY DEFAULT
# ============================================================

NATIVE_TRANSLATION_MODEL_ENABLED = (
    os.getenv(
        "NATIVE_TRANSLATION_MODEL_ENABLED",
        "True",
    )
    .strip()
    .lower()
    in {"1", "true", "yes", "on"}
)

# ============================================================
# MODEL CACHE
# ============================================================

_hi_en_tokenizer = None
_hi_en_model = None

_en_hi_tokenizer = None
_en_hi_model = None

_hi_en_lock = threading.Lock()
_en_hi_lock = threading.Lock()

_hi_en_failed = False
_en_hi_failed = False

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

    "Humayun Tomb": "Humayun's Tomb",
    "Jama Mosque": "Jama Masjid",

    "Akshardham": "Akshardham Temple",
    "Old Fort": "Purana Qila",
    "Lodi Garden": "Lodhi Garden",
}

# ============================================================
# EMERGENCY FALLBACKS ONLY
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

    "मैं खाना खाने जा रहा हूँ":
        "I am going to eat food.",

    "मैं खाना खाने जा रहा हूं":
        "I am going to eat food.",

    "मैं खाना खाने जा रही हूँ":
        "I am going to eat food.",

    "मैं खाना खाने जा रही हूं":
        "I am going to eat food.",
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
# NORMALIZE
# ============================================================

def normalize_text(text):
    if not text:
        return ""

    text = str(text).strip()

    # Remove only punctuation that should not affect matching.
    text = text.replace("।", "")
    text = text.replace("?", "")
    text = text.replace("!", "")

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# CORRECT ENGLISH PLACE NAMES
# ============================================================

def correct_english_place_names(text):

    if not text:
        return text

    for wrong, correct in sorted(
        ENGLISH_PLACE_CORRECTIONS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):

        text = re.sub(
            re.escape(wrong),
            correct,
            text,
            flags=re.IGNORECASE,
        )

    return text.strip()


# ============================================================
# REPLACE HINDI PLACE NAMES
# ONLY USED AS LAST FALLBACK
# ============================================================

def replace_hindi_place_names(text):

    if not text:
        return text

    result = text

    for hindi_place, english_place in sorted(
        HINDI_PLACE_NAMES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):

        result = result.replace(
            hindi_place,
            english_place,
        )

    return result


# ============================================================
# LOAD HINDI -> ENGLISH MODEL
# ============================================================

def _get_hi_en():

    global _hi_en_tokenizer
    global _hi_en_model
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
            "Hindi -> English model is DISABLED."
        )

        return None, None

    if _hi_en_failed:

        print(
            "[NativeLanguage] "
            "Hindi -> English model previously failed."
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

        try:

            print(
                "[NativeLanguage] "
                "Loading REAL Hindi -> English model:"
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
                "REAL Hindi -> English MODEL LOADED."
            )

            return (
                tokenizer,
                model,
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


# ============================================================
# LOAD ENGLISH -> HINDI MODEL
# ============================================================

def _get_en_hi():

    global _en_hi_tokenizer
    global _en_hi_model
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
            "English -> Hindi model is DISABLED."
        )

        return None, None

    if _en_hi_failed:

        print(
            "[NativeLanguage] "
            "English -> Hindi model previously failed."
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

        try:

            print(
                "[NativeLanguage] "
                "Loading REAL English -> Hindi model:"
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
                "REAL English -> Hindi MODEL LOADED."
            )

            return (
                tokenizer,
                model,
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


# ============================================================
# RUN MODEL
# ============================================================

def _run_model(
    tokenizer,
    model,
    text,
):

    import torch

    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
    )

    with torch.no_grad():

        output = model.generate(
            **inputs,
            max_length=128,
            num_beams=4,
            do_sample=False,
        )

    translated = tokenizer.decode(
        output[0],
        skip_special_tokens=True,
    ).strip()

    return translated or None


# ============================================================
# HINDI -> ENGLISH
# ============================================================

def translate_hindi_to_english(text):

    if not text or not str(text).strip():
        return ""

    text = normalize_text(text)

    print(
        "[NativeLanguage] "
        "Hindi -> English request:",
        text,
    )

    # ========================================================
    # REAL ML MODEL FIRST
    # ========================================================

    tokenizer, model = _get_hi_en()

    if (
        tokenizer is not None
        and model is not None
    ):

        try:

            print(
                "[NativeLanguage] "
                "RUNNING REAL ML MODEL..."
            )

            # CRITICAL:
            # Original Hindi goes directly to the model.
            # Do NOT replace Hindi words with English first.

            translated = _run_model(
                tokenizer,
                model,
                text,
            )

            if translated:

                translated = (
                    correct_english_place_names(
                        translated
                    )
                )

                print(
                    "[NativeLanguage] "
                    "REAL MODEL OUTPUT:",
                    translated,
                )

                return translated

        except Exception as error:

            print(
                "[NativeLanguage] "
                "REAL MODEL INFERENCE ERROR:",
                repr(error),
            )

    # ========================================================
    # FALLBACK ONLY AFTER MODEL FAILURE
    # ========================================================

    print(
        "[NativeLanguage] "
        "REAL MODEL FAILED/UNAVAILABLE. "
        "Trying fallback..."
    )

    normalized = normalize_text(text)

    for hindi, english in COMMON_HINDI_FALLBACKS.items():

        if normalize_text(hindi) == normalized:

            return english

    # Generic place fallback.
    for hindi_place, english_place in sorted(
        HINDI_PLACE_NAMES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):

        place = re.escape(hindi_place)

        patterns = [

            (
                rf"^मैं\s+{place}\s+जा\s+रहा\s+हूं$",
                f"I am going to {english_place}.",
            ),

            (
                rf"^मैं\s+{place}\s+जा\s+रहा\s+हूँ$",
                f"I am going to {english_place}.",
            ),

            (
                rf"^मैं\s+{place}\s+जा\s+रही\s+हूं$",
                f"I am going to {english_place}.",
            ),

            (
                rf"^मैं\s+{place}\s+जा\s+रही\s+हूँ$",
                f"I am going to {english_place}.",
            ),

            (
                rf"^मैं\s+{place}\s+देखने\s+जा\s+रहा\s+हूं$",
                f"I am going to see {english_place}.",
            ),

            (
                rf"^मैं\s+{place}\s+देखने\s+जा\s+रहा\s+हूँ$",
                f"I am going to see {english_place}.",
            ),

            (
                rf"^मैं\s+{place}\s+जाना\s+चाहता\s+हूं$",
                f"I want to go to {english_place}.",
            ),

            (
                rf"^मैं\s+{place}\s+जाना\s+चाहता\s+हूँ$",
                f"I want to go to {english_place}.",
            ),
        ]

        for pattern, result in patterns:

            if re.match(
                pattern,
                normalized,
            ):
                return result

    replaced = replace_hindi_place_names(
        text
    )

    if replaced != text:
        return replaced

    return text


# ============================================================
# ENGLISH -> HINDI
# ============================================================

def translate_english_to_hindi(text):

    if not text or not str(text).strip():
        return ""

    text = normalize_text(text)

    print(
        "[NativeLanguage] "
        "English -> Hindi request:",
        text,
    )

    # ========================================================
    # REAL ML MODEL FIRST
    # ========================================================

    tokenizer, model = _get_en_hi()

    if (
        tokenizer is not None
        and model is not None
    ):

        try:

            print(
                "[NativeLanguage] "
                "RUNNING REAL English -> Hindi MODEL..."
            )

            translated = _run_model(
                tokenizer,
                model,
                text,
            )

            if translated:

                print(
                    "[NativeLanguage] "
                    "REAL MODEL OUTPUT:",
                    translated,
                )

                return translated

        except Exception as error:

            print(
                "[NativeLanguage] "
                "REAL English -> Hindi MODEL ERROR:",
                repr(error),
            )

    # ========================================================
    # FALLBACK
    # ========================================================

    normalized = text.lower()

    if normalized in COMMON_ENGLISH_FALLBACKS:

        return COMMON_ENGLISH_FALLBACKS[
            normalized
        ]

    return text


# ============================================================
# AUTO TRANSLATE
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