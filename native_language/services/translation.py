"""
Render-safe translation service for GoPlan Native Language AI.

Default behavior:
- Does NOT load PyTorch models.
- Uses lightweight built-in Hindi/English rules for common travel text.
- Heavy Hugging Face translation models are optional.
- Models are loaded lazily and only once per process.
- Designed to avoid unnecessary downloads and memory usage on small
  Render instances.
"""

import os
import re


# ============================================================
# CONFIGURATION
# ============================================================

HI_EN_MODEL = os.getenv(
    "NATIVE_HI_EN_MODEL",
    "Helsinki-NLP/opus-mt-hi-en",
)

EN_HI_MODEL = os.getenv(
    "NATIVE_EN_HI_MODEL",
    "Helsinki-NLP/opus-mt-en-hi",
)

NATIVE_TRANSLATION_MODEL_ENABLED = (
    os.getenv(
        "NATIVE_TRANSLATION_MODEL_ENABLED",
        "False",
    )
    .strip()
    .lower()
    in {"1", "true", "yes", "on"}
)


# ============================================================
# MODEL STATE
# ============================================================

_hi_en_tokenizer = None
_hi_en_model = None

_en_hi_tokenizer = None
_en_hi_model = None


# ============================================================
# LAZY HINDI → ENGLISH MODEL
# ============================================================

def _get_hi_en():
    global _hi_en_tokenizer
    global _hi_en_model

    if (
        _hi_en_tokenizer is not None
        and _hi_en_model is not None
    ):
        return (
            _hi_en_tokenizer,
            _hi_en_model,
        )

    if not NATIVE_TRANSLATION_MODEL_ENABLED:
        return None, None

    try:
        from transformers import (
            AutoTokenizer,
            AutoModelForSeq2SeqLM,
        )

        _hi_en_tokenizer = AutoTokenizer.from_pretrained(
            HI_EN_MODEL
        )

        _hi_en_model = AutoModelForSeq2SeqLM.from_pretrained(
            HI_EN_MODEL
        )

        return (
            _hi_en_tokenizer,
            _hi_en_model,
        )

    except Exception as error:
        print(
            "[NativeLanguage] Hindi→English model load failed:",
            error,
        )

        _hi_en_tokenizer = None
        _hi_en_model = None

        return None, None


# ============================================================
# LAZY ENGLISH → HINDI MODEL
# ============================================================

def _get_en_hi():
    global _en_hi_tokenizer
    global _en_hi_model

    if (
        _en_hi_tokenizer is not None
        and _en_hi_model is not None
    ):
        return (
            _en_hi_tokenizer,
            _en_hi_model,
        )

    if not NATIVE_TRANSLATION_MODEL_ENABLED:
        return None, None

    try:
        from transformers import (
            AutoTokenizer,
            AutoModelForSeq2SeqLM,
        )

        _en_hi_tokenizer = AutoTokenizer.from_pretrained(
            EN_HI_MODEL
        )

        _en_hi_model = AutoModelForSeq2SeqLM.from_pretrained(
            EN_HI_MODEL
        )

        return (
            _en_hi_tokenizer,
            _en_hi_model,
        )

    except Exception as error:
        print(
            "[NativeLanguage] English→Hindi model load failed:",
            error,
        )

        _en_hi_tokenizer = None
        _en_hi_model = None

        return None, None


# ============================================================
# PLACE NAMES
# ============================================================

HINDI_PLACE_NAMES = {
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

    "दिल्ली": "Delhi",

    "आगरा": "Agra",
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

    "Delhi": "Delhi",
    "Agra": "Agra",
}


# ============================================================
# COMMON HINDI → ENGLISH WORDS
# ============================================================

HINDI_TO_ENGLISH = {
    "मैं": "I",
    "हम": "we",
    "आप": "you",
    "तुम": "you",
    "मुझे": "me",
    "मेरा": "my",
    "मेरी": "my",
    "मेरे": "my",

    "है": "is",
    "हैं": "are",
    "था": "was",
    "थी": "was",
    "थे": "were",

    "यह": "this",
    "वह": "that",
    "यहाँ": "here",
    "वहाँ": "there",

    "क्या": "what",
    "कहाँ": "where",
    "कैसे": "how",
    "क्यों": "why",
    "कब": "when",

    "जाना": "go",
    "जाऊंगा": "I will go",
    "जाऊँगा": "I will go",
    "जाऊंगी": "I will go",
    "जाऊँगी": "I will go",
    "जाता": "go",
    "जाती": "go",
    "जाते": "go",
    "जाओ": "go",

    "देखना": "see",
    "देखने": "see",
    "देखो": "see",

    "बताना": "tell",
    "बताओ": "tell",

    "दिखाना": "show",
    "दिखाओ": "show",

    "चाहिए": "need",

    "आज": "today",
    "कल": "tomorrow",

    "बहुत": "very much",
    "सुंदर": "beautiful",
    "खूबसूरत": "beautiful",
    "जगह": "place",
    "जगहें": "places",

    "घूमना": "travel",
    "घूमने": "travel",
    "घूमो": "travel",

    "और": "and",
    "लेकिन": "but",
    "या": "or",
    "नहीं": "not",
    "हाँ": "yes",
}


# ============================================================
# COMMON ENGLISH → HINDI WORDS
# ============================================================

ENGLISH_TO_HINDI = {
    "i": "मैं",
    "we": "हम",
    "you": "आप",
    "me": "मुझे",
    "my": "मेरा",

    "is": "है",
    "are": "हैं",
    "was": "था",
    "were": "थे",

    "this": "यह",
    "that": "वह",
    "here": "यहाँ",
    "there": "वहाँ",

    "what": "क्या",
    "where": "कहाँ",
    "how": "कैसे",
    "why": "क्यों",
    "when": "कब",

    "go": "जाना",
    "going": "जा रहा हूँ",
    "see": "देखना",
    "tell": "बताना",
    "show": "दिखाना",

    "today": "आज",
    "tomorrow": "कल",

    "beautiful": "सुंदर",
    "place": "जगह",
    "places": "जगहें",

    "travel": "घूमना",

    "and": "और",
    "but": "लेकिन",
    "or": "या",
    "not": "नहीं",
    "yes": "हाँ",
}


# ============================================================
# PLACE CORRECTION
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
            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जा\s+रहा\s+हूं$",
            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जा\s+रहा\s+हूँ$",
            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊंगा$",
            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊँगा$",
            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊंगा$",
            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊँगा$",
            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+जाऊंगा$",
            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+जाऊँगा$",
        ]

        for pattern in patterns:

            if re.match(pattern, text):

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

                if "जाऊंगा" in text or "जाऊँगा" in text:
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
# LIGHTWEIGHT TOKEN TRANSLATION
# ============================================================

def _simple_hindi_to_english(text):
    """
    Lightweight fallback.

    It is intentionally conservative:
    unknown words are preserved instead of being guessed.
    """

    text = text.strip()

    if not text:
        return ""

    known = translate_known_hindi_sentence(text)

    if known:
        return known

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

    words = result.split()
    translated_words = []

    for word in words:
        clean_word = word.strip(
            ".,!?;:()[]{}\"'"
        )

        punctuation_prefix = ""
        punctuation_suffix = ""

        match = re.match(
            r"^([^A-Za-z\u0900-\u097F]*)(.*?)([^A-Za-z\u0900-\u097F]*)$",
            word,
        )

        if match:
            punctuation_prefix = match.group(1)
            core = match.group(2)
            punctuation_suffix = match.group(3)
        else:
            core = word

        translated = HINDI_TO_ENGLISH.get(
            core,
            core,
        )

        translated_words.append(
            punctuation_prefix
            + translated
            + punctuation_suffix
        )

    return correct_english_place_names(
        " ".join(translated_words)
    ).strip()


def _simple_english_to_hindi(text):
    """
    Lightweight fallback for common English travel text.
    Unknown words remain unchanged.
    """

    text = text.strip()

    if not text:
        return ""

    words = text.split()

    translated_words = []

    for word in words:

        match = re.match(
            r"^([^A-Za-z]*)([A-Za-z]+)([^A-Za-z]*)$",
            word,
        )

        if not match:
            translated_words.append(word)
            continue

        prefix = match.group(1)
        core = match.group(2)
        suffix = match.group(3)

        translated = ENGLISH_TO_HINDI.get(
            core.lower(),
            core,
        )

        translated_words.append(
            prefix
            + translated
            + suffix
        )

    return " ".join(
        translated_words
    ).strip()


# ============================================================
# MODEL HINDI → ENGLISH
# ============================================================

def _model_translate_hindi_to_english(text):
    tokenizer, model = _get_hi_en()

    if tokenizer is None or model is None:
        return None

    try:
        import torch

        translated_input = text

        places = sorted(
            HINDI_PLACE_NAMES.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for hindi_place, english_place in places:
            translated_input = translated_input.replace(
                hindi_place,
                english_place,
            )

        inputs = tokenizer(
            translated_input,
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
                early_stopping=True,
            )

        translated = tokenizer.decode(
            output[0],
            skip_special_tokens=True,
        )

        return correct_english_place_names(
            translated
        ).strip()

    except Exception as error:
        print(
            "[NativeLanguage] Hindi→English translation error:",
            error,
        )

        return None


# ============================================================
# MODEL ENGLISH → HINDI
# ============================================================

def _model_translate_english_to_hindi(text):
    tokenizer, model = _get_en_hi()

    if tokenizer is None or model is None:
        return None

    try:
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
                early_stopping=True,
            )

        translated = tokenizer.decode(
            output[0],
            skip_special_tokens=True,
        )

        return translated.strip()

    except Exception as error:
        print(
            "[NativeLanguage] English→Hindi translation error:",
            error,
        )

        return None


# ============================================================
# PUBLIC HINDI → ENGLISH
# ============================================================

def translate_hindi_to_english(text):
    if not text or not text.strip():
        return ""

    text = text.strip()

    # First use local lightweight rules.
    lightweight = _simple_hindi_to_english(
        text
    )

    # If transformer is explicitly enabled,
    # it can improve translations.
    if NATIVE_TRANSLATION_MODEL_ENABLED:

        model_result = _model_translate_hindi_to_english(
            text
        )

        if model_result:
            return model_result

    return lightweight


# ============================================================
# PUBLIC ENGLISH → HINDI
# ============================================================

def translate_english_to_hindi(text):
    if not text or not text.strip():
        return ""

    text = text.strip()

    if NATIVE_TRANSLATION_MODEL_ENABLED:

        model_result = _model_translate_english_to_hindi(
            text
        )

        if model_result:
            return model_result

    return _simple_english_to_hindi(
        text
    )


# ============================================================
# AUTO TRANSLATOR
# ============================================================

def auto_translate(text, detected_language):

    if not text or not text.strip():
        return ""

    text = text.strip()

    if detected_language == "Hindi":
        return translate_hindi_to_english(text)

    if detected_language == "English":
        return translate_english_to_hindi(text)

    return text