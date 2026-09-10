"""
Native Language AI Translation Service

Translation is performed through Hugging Face Inference API.

Direction:
    Hindi -> English
    English -> Hindi

The Hugging Face token MUST stay on the Django/Render server.
Never put HF_TOKEN in frontend JavaScript.
"""

import os
import re
import requests


# ============================================================
# CONFIGURATION
# ============================================================

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()

HI_EN_MODEL = os.getenv(
    "NATIVE_HI_EN_MODEL",
    "Helsinki-NLP/opus-mt-hi-en",
).strip()

EN_HI_MODEL = os.getenv(
    "NATIVE_EN_HI_MODEL",
    "Helsinki-NLP/opus-mt-en-hi",
).strip()


# ============================================================
# HUGGING FACE API
# ============================================================

HF_API_BASE = (
    "https://router.huggingface.co/hf-inference/models/"
)


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
# ENGLISH PLACE CORRECTIONS
# ============================================================

ENGLISH_PLACE_CORRECTIONS = {
    "QUTUB_MAR": "Qutub Minar",
    "QUTUB_MINAR": "Qutub Minar",
    "Qutub Mar": "Qutub Minar",
    "Qutb Minar": "Qutub Minar",
    "Kutub Minar": "Qutub Minar",
    "Kutub Tower": "Qutub Minar",
    "Qutub Tower": "Qutub Minar",

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
# FALLBACKS
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
        "मैं दिल्ली जाना चाहता हूँ。",
}


# ============================================================
# NORMALIZE
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).strip()

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
# PLACE CORRECTION
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
# HF REQUEST
# ============================================================

def _huggingface_translate(text, model_name):

    if not HF_TOKEN:

        print(
            "[NativeLanguage] ERROR: HF_TOKEN not configured."
        )

        return None

    url = HF_API_BASE + model_name

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "inputs": text,
        "options": {
            "wait_for_model": True
        },
    }

    try:

        print(
            "[NativeLanguage] "
            "Calling Hugging Face model:",
            model_name,
        )

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60,
        )

        print(
            "[NativeLanguage] "
            "HF STATUS:",
            response.status_code,
        )

        print(
            "[NativeLanguage] "
            "HF RESPONSE:",
            response.text[:1000],
        )

        if not response.ok:

            print(
                "[NativeLanguage] "
                "HF API ERROR:",
                response.status_code,
            )

            return None

        data = response.json()

        # Typical translation response:
        # [{"translation_text": "..."}]

        if isinstance(data, list) and data:

            item = data[0]

            if isinstance(item, dict):

                translated = (
                    item.get("translation_text")
                    or item.get("generated_text")
                )

                if translated:
                    return str(
                        translated
                    ).strip()

        # Some endpoints/providers can return
        # a direct object.

        if isinstance(data, dict):

            translated = (
                data.get("translation_text")
                or data.get("generated_text")
            )

            if translated:
                return str(
                    translated
                ).strip()

        print(
            "[NativeLanguage] "
            "HF returned no translation."
        )

        return None

    except requests.Timeout:

        print(
            "[NativeLanguage] "
            "HF API TIMEOUT"
        )

        return None

    except Exception as error:

        print(
            "[NativeLanguage] "
            "HF API REQUEST ERROR:",
            repr(error),
        )

        return None


# ============================================================
# HINDI FALLBACK
# ============================================================

def _fallback_hindi_to_english(text):

    normalized = normalize_text(text)

    for hindi, english in COMMON_HINDI_FALLBACKS.items():

        if normalize_text(hindi) == normalized:

            return english

    for hindi_place, english_place in sorted(
        HINDI_PLACE_NAMES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):

        place = re.escape(
            hindi_place
        )

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

        for pattern, translation in patterns:

            if re.match(
                pattern,
                normalized,
            ):
                return translation

    for hindi, english in sorted(
        HINDI_PLACE_NAMES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):

        if hindi in text:

            text = text.replace(
                hindi,
                english,
            )

    return text


# ============================================================
# ENGLISH FALLBACK
# ============================================================

def _fallback_english_to_hindi(text):

    normalized = normalize_text(
        text
    ).lower()

    if normalized in COMMON_ENGLISH_FALLBACKS:

        return COMMON_ENGLISH_FALLBACKS[
            normalized
        ]

    return text


# ============================================================
# HINDI -> ENGLISH
# ============================================================

def translate_hindi_to_english(text):

    if not text or not str(text).strip():
        return ""

    text = normalize_text(text)

    print(
        "\n[NativeLanguage] "
        "HINDI -> ENGLISH:",
        text,
    )

    translated = _huggingface_translate(
        text,
        HI_EN_MODEL,
    )

    if translated:

        translated = (
            correct_english_place_names(
                translated
            )
        )

        print(
            "[NativeLanguage] "
            "HF RESULT:",
            translated,
        )

        return translated

    print(
        "[NativeLanguage] "
        "HF failed. Using fallback."
    )

    return _fallback_hindi_to_english(
        text
    )


# ============================================================
# ENGLISH -> HINDI
# ============================================================

def translate_english_to_hindi(text):

    if not text or not str(text).strip():
        return ""

    text = normalize_text(text)

    print(
        "\n[NativeLanguage] "
        "ENGLISH -> HINDI:",
        text,
    )

    translated = _huggingface_translate(
        text,
        EN_HI_MODEL,
    )

    if translated:

        print(
            "[NativeLanguage] "
            "HF RESULT:",
            translated,
        )

        return translated

    print(
        "[NativeLanguage] "
        "HF failed. Using fallback."
    )

    return _fallback_english_to_hindi(
        text
    )


# ============================================================
# AUTO TRANSLATE
# ============================================================

def auto_translate(
    text,
    detected_language,
):

    if detected_language == "Hindi":

        return translate_hindi_to_english(
            text
        )

    if detected_language == "English":

        return translate_english_to_hindi(
            text
        )

    return text