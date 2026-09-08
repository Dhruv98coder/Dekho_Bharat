"""
Native Language AI - Translation

Original models:
    Hindi -> English:
        Helsinki-NLP/opus-mt-hi-en

    English -> Hindi:
        Helsinki-NLP/opus-mt-en-hi

Design:
- Original Hugging Face models are preserved.
- Models are loaded lazily.
- Each model is loaded once per Django worker.
- Hugging Face cache is reused.
- No force_download.
- PyTorch is imported only when inference is required.
- Existing place-name protection/correction is preserved.
- Model loading errors are handled without crashing the Django process.
"""

import os
import re
import threading


# ============================================================
# MODELS
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
# Default = True
#
# Local machine:
#   True
#
# Render:
#   True if enough memory is available.
#
# If you ever need to temporarily disable translation models:
#
# NATIVE_TRANSLATION_MODEL_ENABLED=False
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

_hi_en_lock = threading.Lock()
_en_hi_lock = threading.Lock()


# ============================================================
# HINDI -> ENGLISH MODEL
# ============================================================

def _get_hi_en():

    global _hi_en_tokenizer
    global _hi_en_model
    global _hi_en_loading

    # Already loaded
    if (
        _hi_en_tokenizer is not None
        and _hi_en_model is not None
    ):
        return (
            _hi_en_tokenizer,
            _hi_en_model,
        )

    # Disabled
    if not NATIVE_TRANSLATION_MODEL_ENABLED:
        return None, None

    with _hi_en_lock:

        # Check again after acquiring lock
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

            from transformers import (
                AutoTokenizer,
                AutoModelForSeq2SeqLM,
            )

            print(
                "[NativeLanguage] "
                "Loading Hindi -> English model..."
            )

            tokenizer = AutoTokenizer.from_pretrained(
                HI_EN_MODEL,
            )

            model = AutoModelForSeq2SeqLM.from_pretrained(
                HI_EN_MODEL,
            )

            model.eval()

            _hi_en_tokenizer = tokenizer
            _hi_en_model = model

            print(
                "[NativeLanguage] "
                "Hindi -> English model loaded."
            )

            return (
                _hi_en_tokenizer,
                _hi_en_model,
            )

        except Exception as error:

            print(
                "[NativeLanguage] "
                "Hindi -> English model load error:",
                repr(error),
            )

            return None, None

        finally:
            _hi_en_loading = False


# ============================================================
# ENGLISH -> HINDI MODEL
# ============================================================

def _get_en_hi():

    global _en_hi_tokenizer
    global _en_hi_model
    global _en_hi_loading

    # Already loaded
    if (
        _en_hi_tokenizer is not None
        and _en_hi_model is not None
    ):
        return (
            _en_hi_tokenizer,
            _en_hi_model,
        )

    # Disabled
    if not NATIVE_TRANSLATION_MODEL_ENABLED:
        return None, None

    with _en_hi_lock:

        # Check again after acquiring lock
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

            from transformers import (
                AutoTokenizer,
                AutoModelForSeq2SeqLM,
            )

            print(
                "[NativeLanguage] "
                "Loading English -> Hindi model..."
            )

            tokenizer = AutoTokenizer.from_pretrained(
                EN_HI_MODEL,
            )

            model = AutoModelForSeq2SeqLM.from_pretrained(
                EN_HI_MODEL,
            )

            model.eval()

            _en_hi_tokenizer = tokenizer
            _en_hi_model = model

            print(
                "[NativeLanguage] "
                "English -> Hindi model loaded."
            )

            return (
                _en_hi_tokenizer,
                _en_hi_model,
            )

        except Exception as error:

            print(
                "[NativeLanguage] "
                "English -> Hindi model load error:",
                repr(error),
            )

            return None, None

        finally:
            _en_hi_loading = False


# ============================================================
# HINDI PLACE NAMES
# ============================================================

HINDI_PLACE_NAMES = {

    "कुतुब मीनार":
        "Qutub Minar",

    "कुतुबमीनार":
        "Qutub Minar",

    "लाल किला":
        "Red Fort",

    "लालकिला":
        "Red Fort",

    "इंडिया गेट":
        "India Gate",

    "इंडियागेट":
        "India Gate",

    "हुमायूं का मकबरा":
        "Humayun's Tomb",

    "कमल मंदिर":
        "Lotus Temple",

    "जामा मस्जिद":
        "Jama Masjid",

    "अक्षरधाम मंदिर":
        "Akshardham Temple",

    "अक्षरधाम":
        "Akshardham Temple",

    "जंतर मंतर":
        "Jantar Mantar",

    "पुराना किला":
        "Purana Qila",

    "लोधी गार्डन":
        "Lodhi Garden",

    "राष्ट्रपति भवन":
        "Rashtrapati Bhavan",

    "राजघाट":
        "Raj Ghat",
}


# ============================================================
# ENGLISH PLACE NAME CORRECTIONS
# ============================================================

ENGLISH_PLACE_CORRECTIONS = {

    "QUTUB_MAR":
        "Qutub Minar",

    "QUTUB_MINAR":
        "Qutub Minar",

    "Qutub Mar":
        "Qutub Minar",

    "Qutub Minar":
        "Qutub Minar",

    "Qutb Minar":
        "Qutub Minar",

    "Kutub Minar":
        "Qutub Minar",

    "Kutub Tower":
        "Qutub Minar",

    "Qutub Tower":
        "Qutub Minar",

    "Kutble Tower":
        "Qutub Minar",

    "Kuthble Tower":
        "Qutub Minar",

    "RED_FORT":
        "Red Fort",

    "PALCHOLDER0":
        "Red Fort",

    "PALHOLDER0":
        "Red Fort",

    "PALCHOLDER":
        "Red Fort",

    "Red Kila":
        "Red Fort",

    "Lal Kila":
        "Red Fort",

    "Lal Qila":
        "Red Fort",

    "India Gate":
        "India Gate",

    "Humayun Tomb":
        "Humayun's Tomb",

    "Humayun's Tomb":
        "Humayun's Tomb",

    "Lotus Temple":
        "Lotus Temple",

    "Jama Mosque":
        "Jama Masjid",

    "Jama Masjid":
        "Jama Masjid",

    "Akshardham":
        "Akshardham Temple",

    "Akshardham Temple":
        "Akshardham Temple",

    "Jantar Mantar":
        "Jantar Mantar",

    "Old Fort":
        "Purana Qila",

    "Purana Qila":
        "Purana Qila",

    "Lodi Garden":
        "Lodhi Garden",

    "Lodhi Garden":
        "Lodhi Garden",

    "Rashtrapati Bhavan":
        "Rashtrapati Bhavan",

    "Raj Ghat":
        "Raj Ghat",
}


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
# SPECIAL HINDI SENTENCES
# ============================================================

def translate_known_hindi_sentence(text):

    text = text.strip()

    for hindi_place, english_place in HINDI_PLACE_NAMES.items():

        patterns = [

            # मैं <PLACE> देखने जा रहा हूं
            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जा\s+रहा\s+हूं$",

            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जा\s+रहा\s+हूँ$",

            # मैं <PLACE> देखने जाऊंगा
            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊंगा$",

            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊँगा$",

            # आज मैं <PLACE> देखने जाऊंगा
            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊंगा$",

            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊँगा$",

            # आज मैं <PLACE> जाऊंगा
            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+जाऊंगा$",

            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+जाऊँगा$",

            # मैं <PLACE> देखने जाऊंगा कल
            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊंगा\s+कल$",

            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊँगा\s+कल$",
        ]

        for pattern in patterns:

            if not re.match(pattern, text):
                continue

            if (
                "जाऊंगा" in text
                or "जाऊँगा" in text
            ):

                if "कल" in text:
                    return (
                        f"I will go to see "
                        f"{english_place} tomorrow."
                    )

                if "आज" in text:

                    if "देखने" in text:
                        return (
                            f"Today I will go to see "
                            f"{english_place}."
                        )

                    return (
                        f"Today I will go to "
                        f"{english_place}."
                    )

                return (
                    f"I will go to see "
                    f"{english_place}."
                )

            return (
                f"I am going to see "
                f"{english_place}."
            )

    return None


# ============================================================
# REPLACE HINDI PLACE NAMES
# ============================================================

def replace_hindi_place_names(text):

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
# HINDI -> ENGLISH
# ============================================================

def translate_hindi_to_english(text):

    if not text or not text.strip():
        return ""

    text = text.strip()

    # --------------------------------------------------------
    # Known sentence first.
    # This avoids unnecessary model loading for known patterns.
    # --------------------------------------------------------

    known_translation = (
        translate_known_hindi_sentence(
            text
        )
    )

    if known_translation:
        return known_translation

    # --------------------------------------------------------
    # Load original model
    # --------------------------------------------------------

    tokenizer, model = _get_hi_en()

    if tokenizer is None or model is None:

        # Do NOT crash Django.
        # Return original text if model cannot be loaded.
        print(
            "[NativeLanguage] "
            "Hindi -> English model unavailable."
        )

        return text

    # --------------------------------------------------------
    # Preserve known place names
    # --------------------------------------------------------

    translated_input = (
        replace_hindi_place_names(
            text
        )
    )

    # --------------------------------------------------------
    # Tokenize
    # --------------------------------------------------------

    try:

        inputs = tokenizer(
            translated_input,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128,
        )

        # ----------------------------------------------------
        # Generate
        # ----------------------------------------------------

        import torch

        with torch.no_grad():

            output = model.generate(
                **inputs,
                max_length=128,
                num_beams=8,
                do_sample=False,
                early_stopping=True,
            )

        # ----------------------------------------------------
        # Decode
        # ----------------------------------------------------

        translated = tokenizer.decode(
            output[0],
            skip_special_tokens=True,
        )

        # ----------------------------------------------------
        # Correct place names
        # ----------------------------------------------------

        translated = (
            correct_english_place_names(
                translated
            )
        )

        return translated.strip()

    except Exception as error:

        print(
            "[NativeLanguage] "
            "Hindi -> English inference error:",
            repr(error),
        )

        return text


# ============================================================
# ENGLISH -> HINDI
# ============================================================

def translate_english_to_hindi(text):

    if not text or not text.strip():
        return ""

    text = text.strip()

    # --------------------------------------------------------
    # Load original model
    # --------------------------------------------------------

    tokenizer, model = _get_en_hi()

    if tokenizer is None or model is None:

        print(
            "[NativeLanguage] "
            "English -> Hindi model unavailable."
        )

        return text

    # --------------------------------------------------------
    # Translate
    # --------------------------------------------------------

    try:

        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128,
        )

        import torch

        with torch.no_grad():

            output = model.generate(
                **inputs,
                max_length=128,
                num_beams=5,
                do_sample=False,
                early_stopping=True,
            )

        translated = tokenizer.decode(
            output[0],
            skip_special_tokens=True,
        )

        return translated.strip()

    except Exception as error:

        print(
            "[NativeLanguage] "
            "English -> Hindi inference error:",
            repr(error),
        )

        return text


# ============================================================
# AUTO TRANSLATOR
# ============================================================

def auto_translate(
    text,
    detected_language,
):

    if not text or not text.strip():
        return ""

    text = text.strip()

    if detected_language == "Hindi":

        return translate_hindi_to_english(
            text
        )

    if detected_language == "English":

        return translate_english_to_hindi(
            text
        )

    return text