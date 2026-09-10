"""
Native Language AI - Translation Service

Render-safe Hindi <-> English translation service.

IMPORTANT:
- Lightweight/common Hindi sentences are translated without loading
  Hugging Face / PyTorch models.
- Hugging Face translation models remain available, but are disabled by
  default to keep the Django Render deployment stable.
- To enable them explicitly:
      NATIVE_TRANSLATION_MODEL_ENABLED=True
"""

import os
import re
import threading


# ============================================================
# MODEL NAMES
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
# Default is FALSE for Render stability.
#
# Local machine:
#   You may set True if you want Hugging Face models.
#
# Render:
#   Keep False for the demo unless the service has enough RAM.
#
# ============================================================

NATIVE_TRANSLATION_MODEL_ENABLED = (
    os.getenv(
        "NATIVE_TRANSLATION_MODEL_ENABLED",
        "False",
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
# COMMON HINDI -> ENGLISH PHRASES
# ============================================================

COMMON_HINDI_PHRASES = {
    "नमस्ते": "Hello.",
    "हेलो": "Hello.",
    "धन्यवाद": "Thank you.",
    "शुक्रिया": "Thank you.",
    "मुझे दिल्ली जाना है": "I want to go to Delhi.",
    "मैं दिल्ली जाना चाहता हूँ": "I want to go to Delhi.",
    "मैं दिल्ली जाना चाहती हूँ": "I want to go to Delhi.",
    "मैं दिल्ली जा रहा हूँ": "I am going to Delhi.",
    "मैं दिल्ली जा रहा हूं": "I am going to Delhi.",
    "मैं दिल्ली जा रही हूँ": "I am going to Delhi.",
    "मैं दिल्ली जा रही हूं": "I am going to Delhi.",
    "मैं दिल्ली घूमने जा रहा हूँ": "I am going to Delhi for sightseeing.",
    "मैं दिल्ली घूमने जा रहा हूं": "I am going to Delhi for sightseeing.",
    "मैं दिल्ली घूमने जा रही हूँ": "I am going to Delhi for sightseeing.",
    "मैं दिल्ली घूमने जा रही हूं": "I am going to Delhi for sightseeing.",
    "आज मैं दिल्ली जा रहा हूँ": "Today I am going to Delhi.",
    "आज मैं दिल्ली जा रहा हूं": "Today I am going to Delhi.",
    "आज मैं दिल्ली जा रही हूँ": "Today I am going to Delhi.",
    "आज मैं दिल्ली जा रही हूं": "Today I am going to Delhi.",
}


# ============================================================
# SIMPLE ENGLISH -> HINDI PHRASES
# ============================================================

COMMON_ENGLISH_PHRASES = {
    "hello": "नमस्ते।",
    "hi": "नमस्ते।",
    "thank you": "धन्यवाद।",
    "thanks": "धन्यवाद।",
    "i want to go to delhi": "मैं दिल्ली जाना चाहता हूँ।",
    "i am going to delhi": "मैं दिल्ली जा रहा हूँ।",
    "i am going to delhi for sightseeing":
        "मैं दिल्ली घूमने जा रहा हूँ।",
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text):
    if not text:
        return ""

    text = str(text).strip()

    # Normalize common Unicode punctuation.
    replacements = {
        "।": "",
        "?": "",
        "!": "",
        "،": ",",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Collapse multiple spaces.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


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
# REPLACE HINDI PLACE NAMES
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
# LIGHTWEIGHT HINDI SENTENCE TRANSLATION
# ============================================================

def translate_known_hindi_sentence(text):
    """
    Translate common travel sentences without Transformers/PyTorch.

    This is the important Render-safe layer.
    """

    if not text:
        return None

    original = str(text).strip()
    normalized = normalize_text(original)

    if not normalized:
        return None

    # --------------------------------------------------------
    # Exact common phrases
    # --------------------------------------------------------

    for hindi, english in COMMON_HINDI_PHRASES.items():
        if normalize_text(hindi) == normalized:
            return english

    # --------------------------------------------------------
    # Pattern-based place handling
    # --------------------------------------------------------

    for hindi_place, english_place in sorted(
        HINDI_PLACE_NAMES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):

        place = re.escape(hindi_place)

        # ----------------------------------------------------
        # मैं <PLACE> देखने जा रहा हूँ
        # ----------------------------------------------------

        patterns_male_present = [
            rf"^मैं\s+{place}\s+देखने\s+जा\s+रहा\s+हूं$",
            rf"^मैं\s+{place}\s+देखने\s+जा\s+रहा\s+हूँ$",
        ]

        for pattern in patterns_male_present:
            if re.match(pattern, normalized):
                return f"I am going to see {english_place}."

        # ----------------------------------------------------
        # मैं <PLACE> देखने जा रही हूँ
        # ----------------------------------------------------

        patterns_female_present = [
            rf"^मैं\s+{place}\s+देखने\s+जा\s+रही\s+हूं$",
            rf"^मैं\s+{place}\s+देखने\s+जा\s+रही\s+हूँ$",
        ]

        for pattern in patterns_female_present:
            if re.match(pattern, normalized):
                return f"I am going to see {english_place}."

        # ----------------------------------------------------
        # मैं <PLACE> जा रहा हूँ
        # ----------------------------------------------------

        patterns_male_going = [
            rf"^मैं\s+{place}\s+जा\s+रहा\s+हूं$",
            rf"^मैं\s+{place}\s+जा\s+रहा\s+हूँ$",
        ]

        for pattern in patterns_male_going:
            if re.match(pattern, normalized):
                return f"I am going to {english_place}."

        # ----------------------------------------------------
        # मैं <PLACE> जा रही हूँ
        # ----------------------------------------------------

        patterns_female_going = [
            rf"^मैं\s+{place}\s+जा\s+रही\s+हूं$",
            rf"^मैं\s+{place}\s+जा\s+रही\s+हूँ$",
        ]

        for pattern in patterns_female_going:
            if re.match(pattern, normalized):
                return f"I am going to {english_place}."

        # ----------------------------------------------------
        # मैं <PLACE> जाना चाहता हूँ
        # ----------------------------------------------------

        patterns_want_male = [
            rf"^मैं\s+{place}\s+जाना\s+चाहता\s+हूं$",
            rf"^मैं\s+{place}\s+जाना\s+चाहता\s+हूँ$",
        ]

        for pattern in patterns_want_male:
            if re.match(pattern, normalized):
                return f"I want to go to {english_place}."

        # ----------------------------------------------------
        # मैं <PLACE> जाना चाहती हूँ
        # ----------------------------------------------------

        patterns_want_female = [
            rf"^मैं\s+{place}\s+जाना\s+चाहती\s+हूं$",
            rf"^मैं\s+{place}\s+जाना\s+चाहती\s+हूँ$",
        ]

        for pattern in patterns_want_female:
            if re.match(pattern, normalized):
                return f"I want to go to {english_place}."

        # ----------------------------------------------------
        # मैं <PLACE> घूमने जा रहा हूँ
        # ----------------------------------------------------

        patterns_sightseeing_male = [
            rf"^मैं\s+{place}\s+घूमने\s+जा\s+रहा\s+हूं$",
            rf"^मैं\s+{place}\s+घूमने\s+जा\s+रहा\s+हूँ$",
        ]

        for pattern in patterns_sightseeing_male:
            if re.match(pattern, normalized):
                return (
                    f"I am going to {english_place} "
                    f"for sightseeing."
                )

        # ----------------------------------------------------
        # मैं <PLACE> घूमने जा रही हूँ
        # ----------------------------------------------------

        patterns_sightseeing_female = [
            rf"^मैं\s+{place}\s+घूमने\s+जा\s+रही\s+हूं$",
            rf"^मैं\s+{place}\s+घूमने\s+जा\s+रही\s+हूँ$",
        ]

        for pattern in patterns_sightseeing_female:
            if re.match(pattern, normalized):
                return (
                    f"I am going to {english_place} "
                    f"for sightseeing."
                )

        # ----------------------------------------------------
        # आज मैं <PLACE> जा रहा हूँ
        # ----------------------------------------------------

        patterns_today_male = [
            rf"^आज\s+मैं\s+{place}\s+जा\s+रहा\s+हूं$",
            rf"^आज\s+मैं\s+{place}\s+जा\s+रहा\s+हूँ$",
        ]

        for pattern in patterns_today_male:
            if re.match(pattern, normalized):
                return f"Today I am going to {english_place}."

        # ----------------------------------------------------
        # आज मैं <PLACE> जा रही हूँ
        # ----------------------------------------------------

        patterns_today_female = [
            rf"^आज\s+मैं\s+{place}\s+जा\s+रही\s+हूं$",
            rf"^आज\s+मैं\s+{place}\s+जा\s+रही\s+हूँ$",
        ]

        for pattern in patterns_today_female:
            if re.match(pattern, normalized):
                return f"Today I am going to {english_place}."

        # ----------------------------------------------------
        # मैं <PLACE> देखने जाऊंगा
        # ----------------------------------------------------

        patterns_future_male = [
            rf"^मैं\s+{place}\s+देखने\s+जाऊंगा$",
            rf"^मैं\s+{place}\s+देखने\s+जाऊँगा$",
        ]

        for pattern in patterns_future_male:
            if re.match(pattern, normalized):
                return f"I will go to see {english_place}."

        # ----------------------------------------------------
        # मैं <PLACE> देखने जाऊंगी
        # ----------------------------------------------------

        patterns_future_female = [
            rf"^मैं\s+{place}\s+देखने\s+जाऊंगी$",
            rf"^मैं\s+{place}\s+देखने\s+जाऊँगी$",
        ]

        for pattern in patterns_future_female:
            if re.match(pattern, normalized):
                return f"I will go to see {english_place}."

        # ----------------------------------------------------
        # आज मैं <PLACE> देखने जाऊंगा
        # ----------------------------------------------------

        patterns_today_future_male = [
            rf"^आज\s+मैं\s+{place}\s+देखने\s+जाऊंगा$",
            rf"^आज\s+मैं\s+{place}\s+देखने\s+जाऊँगा$",
        ]

        for pattern in patterns_today_future_male:
            if re.match(pattern, normalized):
                return (
                    f"Today I will go to see "
                    f"{english_place}."
                )

        # ----------------------------------------------------
        # आज मैं <PLACE> देखने जाऊंगी
        # ----------------------------------------------------

        patterns_today_future_female = [
            rf"^आज\s+मैं\s+{place}\s+देखने\s+जाऊंगी$",
            rf"^आज\s+मैं\s+{place}\s+देखने\s+जाऊँगी$",
        ]

        for pattern in patterns_today_future_female:
            if re.match(pattern, normalized):
                return (
                    f"Today I will go to see "
                    f"{english_place}."
                )

        # ----------------------------------------------------
        # मैं <PLACE> देखने जा रहा हूं कल
        # ----------------------------------------------------

        patterns_tomorrow_male = [
            rf"^मैं\s+{place}\s+देखने\s+जा\s+रहा\s+हूं\s+कल$",
            rf"^मैं\s+{place}\s+देखने\s+जा\s+रहा\s+हूँ\s+कल$",
        ]

        for pattern in patterns_tomorrow_male:
            if re.match(pattern, normalized):
                return (
                    f"I am going to see "
                    f"{english_place} tomorrow."
                )

        # ----------------------------------------------------
        # मैं <PLACE> देखने जा रही हूं कल
        # ----------------------------------------------------

        patterns_tomorrow_female = [
            rf"^मैं\s+{place}\s+देखने\s+जा\s+रही\s+हूं\s+कल$",
            rf"^मैं\s+{place}\s+देखने\s+जा\s+रही\s+हूँ\s+कल$",
        ]

        for pattern in patterns_tomorrow_female:
            if re.match(pattern, normalized):
                return (
                    f"I am going to see "
                    f"{english_place} tomorrow."
                )

    return None


# ============================================================
# GET HINDI -> ENGLISH MODEL
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

        # Re-check
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
                HI_EN_MODEL
            )

            model = AutoModelForSeq2SeqLM.from_pretrained(
                HI_EN_MODEL
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
# GET ENGLISH -> HINDI MODEL
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

        # Re-check
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
                EN_HI_MODEL
            )

            model = AutoModelForSeq2SeqLM.from_pretrained(
                EN_HI_MODEL
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
# HINDI -> ENGLISH
# ============================================================

def translate_hindi_to_english(text):

    if not text or not str(text).strip():
        return ""

    text = str(text).strip()

    # --------------------------------------------------------
    # 1. Lightweight translation first
    # --------------------------------------------------------

    known_translation = (
        translate_known_hindi_sentence(text)
    )

    if known_translation:
        return known_translation

    # --------------------------------------------------------
    # 2. Try original Hugging Face model only if enabled
    # --------------------------------------------------------

    tokenizer, model = _get_hi_en()

    if tokenizer is None or model is None:

        print(
            "[NativeLanguage] "
            "Hindi -> English model disabled/unavailable."
        )

        # ----------------------------------------------------
        # Lightweight place replacement as last safe fallback
        # ----------------------------------------------------

        replaced = replace_hindi_place_names(text)

        if replaced != text:
            return replaced

        return text

    # --------------------------------------------------------
    # 3. Model inference
    # --------------------------------------------------------

    translated_input = replace_hindi_place_names(
        text
    )

    try:

        inputs = tokenizer(
            translated_input,
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
                num_beams=8,
                do_sample=False,
                early_stopping=True,
            )

        translated = tokenizer.decode(
            output[0],
            skip_special_tokens=True,
        )

        translated = correct_english_place_names(
            translated
        )

        return translated.strip()

    except Exception as error:

        print(
            "[NativeLanguage] "
            "Hindi -> English inference error:",
            repr(error),
        )

        # Never break the Django request.
        replaced = replace_hindi_place_names(text)

        if replaced != text:
            return replaced

        return text


# ============================================================
# ENGLISH -> HINDI
# ============================================================

def translate_english_to_hindi(text):

    if not text or not str(text).strip():
        return ""

    text = str(text).strip()

    normalized = normalize_text(
        text
    ).lower()

    # --------------------------------------------------------
    # 1. Lightweight known phrases
    # --------------------------------------------------------

    if normalized in COMMON_ENGLISH_PHRASES:
        return COMMON_ENGLISH_PHRASES[
            normalized
        ]

    # --------------------------------------------------------
    # 2. Model if explicitly enabled
    # --------------------------------------------------------

    tokenizer, model = _get_en_hi()

    if tokenizer is None or model is None:

        # English already received.
        # Keep it intact rather than breaking the API.
        print(
            "[NativeLanguage] "
            "English -> Hindi model disabled/unavailable."
        )

        return text

    # --------------------------------------------------------
    # 3. Model inference
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
                num_beams=8,
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

    if not text or not str(text).strip():
        return ""

    text = str(text).strip()

    if detected_language == "Hindi":
        return translate_hindi_to_english(
            text
        )

    if detected_language == "English":
        return translate_english_to_hindi(
            text
        )

    return text