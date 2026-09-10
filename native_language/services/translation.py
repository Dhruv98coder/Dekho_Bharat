"""
Native Language AI Translation Service

Architecture:
    Django / Render
        ↓
    Hugging Face Inference API
        ↓
    Hindi <-> English translation

Important:
    - HF_TOKEN must exist in Render Environment Variables.
    - Token must NEVER be placed in frontend JavaScript.
    - This file does NOT load Torch/Transformers locally.
"""

import os
import re
import requests


# ============================================================
# CONFIGURATION
# ============================================================

HF_TOKEN = os.getenv(
    "HF_TOKEN",
    ""
).strip()


HI_EN_MODEL = os.getenv(
    "NATIVE_HI_EN_MODEL",
    "Helsinki-NLP/opus-mt-hi-en",
).strip()


EN_HI_MODEL = os.getenv(
    "NATIVE_EN_HI_MODEL",
    "Helsinki-NLP/opus-mt-en-hi",
).strip()


HF_API_BASE = (
    "https://router.huggingface.co/"
    "hf-inference/models/"
)


# ============================================================
# HINDI PLACE NAMES
# ============================================================

HINDI_PLACE_NAMES = {

    "दिल्ली":
        "Delhi",

    "कुतुब मीनार":
        "Qutub Minar",

    "कुतुबमीनार":
        "Qutub Minar",

    "कुतुब":
        "Qutub",

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

    "हुमायूँ का मकबरा":
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

    "ताज महल":
        "Taj Mahal",

    "आगरा":
        "Agra",

    "आगरा किला":
        "Agra Fort",

    "कनॉट प्लेस":
        "Connaught Place",
}


# ============================================================
# ENGLISH PLACE NAMES -> HINDI
#
# Used when Hindi sentence contains English place names.
#
# Example:
#
#     मैं आज Delhi जा रहा हूं
#
# becomes:
#
#     मैं आज दिल्ली जा रहा हूं
# ============================================================

ENGLISH_TO_HINDI_PLACES = {

    "Qutub Minar":
        "कुतुब मीनार",

    "Qutb Minar":
        "कुतुब मीनार",

    "Qutub":
        "कुतुब",

    "Red Fort":
        "लाल किला",

    "Lal Qila":
        "लाल किला",

    "India Gate":
        "इंडिया गेट",

    "Taj Mahal":
        "ताज महल",

    "Agra Fort":
        "आगरा किला",

    "Humayun's Tomb":
        "हुमायूं का मकबरा",

    "Humayuns Tomb":
        "हुमायूं का मकबरा",

    "Lotus Temple":
        "कमल मंदिर",

    "Akshardham Temple":
        "अक्षरधाम मंदिर",

    "Akshardham":
        "अक्षरधाम",

    "Jama Masjid":
        "जामा मस्जिद",

    "Jantar Mantar":
        "जंतर मंतर",

    "Purana Qila":
        "पुराना किला",

    "Lodhi Garden":
        "लोधी गार्डन",

    "Lodi Garden":
        "लोधी गार्डन",

    "Safdarjung Tomb":
        "सफदरजंग का मकबरा",

    "Connaught Place":
        "कनॉट प्लेस",

    "Rashtrapati Bhavan":
        "राष्ट्रपति भवन",

    "Parliament House":
        "संसद भवन",

    "Gateway of India":
        "गेटवे ऑफ इंडिया",

    "Victoria Memorial":
        "विक्टोरिया मेमोरियल",

    "Delhi":
        "दिल्ली",

    "Agra":
        "आगरा",
}


# ============================================================
# ENGLISH OUTPUT CORRECTIONS
# ============================================================

ENGLISH_PLACE_CORRECTIONS = {

    "QUTUB_MAR":
        "Qutub Minar",

    "QUTUB_MINAR":
        "Qutub Minar",

    "Qutub Mar":
        "Qutub Minar",

    "Qutb Minar":
        "Qutub Minar",

    "Kutub Minar":
        "Qutub Minar",

    "Kutub Tower":
        "Qutub Minar",

    "Qutub Tower":
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

    "Humayun Tomb":
        "Humayun's Tomb",

    "Jama Mosque":
        "Jama Masjid",

    "Akshardham":
        "Akshardham Temple",

    "Old Fort":
        "Purana Qila",

    "Lodi Garden":
        "Lodhi Garden",
}


# ============================================================
# COMMON FALLBACKS
# ============================================================

COMMON_HINDI_FALLBACKS = {

    "नमस्ते":
        "Hello.",

    "धन्यवाद":
        "Thank you.",

    "शुक्रिया":
        "Thank you.",

    "मैं दिल्ली जा रहा हूँ":
        "I am going to Delhi.",

    "मैं दिल्ली जा रहा हूं":
        "I am going to Delhi.",

    "मैं दिल्ली जा रही हूँ":
        "I am going to Delhi.",

    "मैं दिल्ली जा रही हूं":
        "I am going to Delhi.",

    "मैं आज दिल्ली जा रहा हूँ":
        "I am going to Delhi today.",

    "मैं आज दिल्ली जा रहा हूं":
        "I am going to Delhi today.",

    "मैं आज दिल्ली जा रही हूँ":
        "I am going to Delhi today.",

    "मैं आज दिल्ली जा रही हूं":
        "I am going to Delhi today.",

    "आज मैं दिल्ली जा रहा हूँ":
        "Today I am going to Delhi.",

    "आज मैं दिल्ली जा रहा हूं":
        "Today I am going to Delhi.",

    "आज मैं दिल्ली जा रही हूँ":
        "Today I am going to Delhi.",

    "आज मैं दिल्ली जा रही हूं":
        "Today I am going to Delhi.",

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

    "hello":
        "नमस्ते।",

    "hi":
        "नमस्ते।",

    "thank you":
        "धन्यवाद।",

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

    text = text.replace(
        "।",
        "",
    )

    text = text.replace(
        "?",
        "",
    )

    text = text.replace(
        "!",
        "",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# MIXED HINDI + ENGLISH PLACE NORMALIZATION
# ============================================================

def normalize_mixed_hindi(text):

    """
    Convert known English place names inside Hindi sentences
    to Hindi script.

    Example:

        मैं आज Delhi जा रहा हूं

    becomes:

        मैं आज दिल्ली जा रहा हूं
    """

    if not text:
        return ""

    result = text

    sorted_places = sorted(
        ENGLISH_TO_HINDI_PLACES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for english, hindi in sorted_places:

        result = re.sub(
            re.escape(english),
            hindi,
            result,
            flags=re.IGNORECASE,
        )

    return result.strip()


# ============================================================
# CORRECT ENGLISH MODEL OUTPUT
# ============================================================

def correct_english_place_names(text):

    if not text:
        return ""

    result = text

    for wrong, correct in sorted(
        ENGLISH_PLACE_CORRECTIONS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):

        result = re.sub(
            re.escape(wrong),
            correct,
            result,
            flags=re.IGNORECASE,
        )

    return result.strip()


# ============================================================
# CONVERT HINDI PLACE NAMES IN ENGLISH OUTPUT
# ============================================================

def normalize_translation_output(text):

    if not text:
        return ""

    result = correct_english_place_names(
        text
    )

    for hindi, english in sorted(
        HINDI_PLACE_NAMES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):

        result = result.replace(
            hindi,
            english,
        )

    return result.strip()


# ============================================================
# HUGGING FACE API
# ============================================================

def _huggingface_translate(
    text,
    model_name,
):

    if not HF_TOKEN:

        print(
            "[NativeLanguage] "
            "ERROR: HF_TOKEN is missing."
        )

        return None

    url = (
        HF_API_BASE +
        model_name
    )

    headers = {

        "Authorization":
            f"Bearer {HF_TOKEN}",

        "Content-Type":
            "application/json",

        "Accept":
            "application/json",
    }

    payload = {

        "inputs":
            text,

        "options": {
            "wait_for_model": True,
        },
    }

    try:

        print(
            "[NativeLanguage] "
            "HF MODEL:",
            model_name,
        )

        print(
            "[NativeLanguage] "
            "HF INPUT:",
            text,
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
                "HF REQUEST FAILED:",
                response.status_code,
            )

            return None

        data = response.json()

        # ----------------------------------------------------
        # Normal translation response
        # ----------------------------------------------------

        if isinstance(
            data,
            list,
        ):

            for item in data:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                translated = (
                    item.get(
                        "translation_text"
                    )
                    or
                    item.get(
                        "generated_text"
                    )
                )

                if translated:

                    return str(
                        translated
                    ).strip()

        # ----------------------------------------------------
        # Object response
        # ----------------------------------------------------

        if isinstance(
            data,
            dict,
        ):

            translated = (
                data.get(
                    "translation_text"
                )
                or
                data.get(
                    "generated_text"
                )
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
            "HF request timed out."
        )

        return None

    except requests.RequestException as error:

        print(
            "[NativeLanguage] "
            "HF network error:",
            repr(error),
        )

        return None

    except Exception as error:

        print(
            "[NativeLanguage] "
            "HF unexpected error:",
            repr(error),
        )

        return None


# ============================================================
# FIND KNOWN HINDI FALLBACK
# ============================================================

def find_known_hindi_fallback(text):

    normalized = normalize_text(
        text
    )

    normalized = normalize_mixed_hindi(
        normalized
    )

    # --------------------------------------------------------
    # Exact known sentence
    # --------------------------------------------------------

    for hindi, english in (
        COMMON_HINDI_FALLBACKS.items()
    ):

        if (
            normalize_text(hindi)
            == normalized
        ):

            return english

    # --------------------------------------------------------
    # Generic "मैं [PLACE] जा रहा हूं"
    # --------------------------------------------------------

    for hindi_place, english_place in sorted(
        HINDI_PLACE_NAMES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):

        place = re.escape(
            hindi_place
        )

        patterns = [

            # ----------------------------------------------
            # मैं दिल्ली जा रहा हूं
            # ----------------------------------------------

            (
                rf"^मैं\s+{place}\s+जा\s+रहा\s+हूं$",
                f"I am going to {english_place}.",
            ),

            (
                rf"^मैं\s+{place}\s+जा\s+रहा\s+हूँ$",
                f"I am going to {english_place}.",
            ),

            # ----------------------------------------------
            # मैं आज दिल्ली जा रहा हूं
            # ----------------------------------------------

            (
                rf"^मैं\s+आज\s+{place}\s+जा\s+रहा\s+हूं$",
                f"I am going to {english_place} today.",
            ),

            (
                rf"^मैं\s+आज\s+{place}\s+जा\s+रहा\s+हूँ$",
                f"I am going to {english_place} today.",
            ),

            # ----------------------------------------------
            # आज मैं दिल्ली जा रहा हूं
            # ----------------------------------------------

            (
                rf"^आज\s+मैं\s+{place}\s+जा\s+रहा\s+हूं$",
                f"Today I am going to {english_place}.",
            ),

            (
                rf"^आज\s+मैं\s+{place}\s+जा\s+रहा\s+हूँ$",
                f"Today I am going to {english_place}.",
            ),

            # ----------------------------------------------
            # Female forms
            # ----------------------------------------------

            (
                rf"^मैं\s+{place}\s+जा\s+रही\s+हूं$",
                f"I am going to {english_place}.",
            ),

            (
                rf"^मैं\s+{place}\s+जा\s+रही\s+हूँ$",
                f"I am going to {english_place}.",
            ),

            (
                rf"^मैं\s+आज\s+{place}\s+जा\s+रही\s+हूं$",
                f"I am going to {english_place} today.",
            ),

            (
                rf"^मैं\s+आज\s+{place}\s+जा\s+रही\s+हूँ$",
                f"I am going to {english_place} today.",
            ),

            (
                rf"^आज\s+मैं\s+{place}\s+जा\s+रही\s+हूं$",
                f"Today I am going to {english_place}.",
            ),

            (
                rf"^आज\s+मैं\s+{place}\s+जा\s+रही\s+हूँ$",
                f"Today I am going to {english_place}.",
            ),

            # ----------------------------------------------
            # देखना
            # ----------------------------------------------

            (
                rf"^मैं\s+{place}\s+देखने\s+जा\s+रहा\s+हूं$",
                f"I am going to see {english_place}.",
            ),

            (
                rf"^मैं\s+{place}\s+देखने\s+जा\s+रहा\s+हूँ$",
                f"I am going to see {english_place}.",
            ),

            # ----------------------------------------------
            # जाना चाहता हूं
            # ----------------------------------------------

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

    return None


# ============================================================
# HINDI -> ENGLISH
# ============================================================

def translate_hindi_to_english(text):

    if not text or not str(text).strip():

        return ""

    original_text = normalize_text(
        text
    )

    print(
        "\n========================================"
    )

    print(
        "[NativeLanguage] "
        "HINDI -> ENGLISH"
    )

    print(
        "[NativeLanguage] ORIGINAL:",
        original_text,
    )

    # ========================================================
    # STEP 1:
    # Normalize mixed English place names
    # ========================================================

    model_input = normalize_mixed_hindi(
        original_text
    )

    print(
        "[NativeLanguage] "
        "NORMALIZED:",
        model_input,
    )

    # ========================================================
    # STEP 2:
    # Deterministic known sentence
    #
    # This is checked BEFORE API so known sentences do not
    # change randomly because of provider/model output.
    # ========================================================

    known_result = find_known_hindi_fallback(
        model_input
    )

    if known_result:

        print(
            "[NativeLanguage] "
            "KNOWN SENTENCE RESULT:",
            known_result,
        )

        print(
            "========================================\n"
        )

        return known_result

    # ========================================================
    # STEP 3:
    # Hugging Face
    # ========================================================

    translated = _huggingface_translate(
        model_input,
        HI_EN_MODEL,
    )

    if translated:

        translated = normalize_translation_output(
            translated
        )

        print(
            "[NativeLanguage] "
            "HF FINAL RESULT:",
            translated,
        )

        print(
            "========================================\n"
        )

        return translated

    # ========================================================
    # STEP 4:
    # Final fallback
    # ========================================================

    fallback = find_known_hindi_fallback(
        model_input
    )

    if fallback:

        return fallback

    # Replace known Hindi places at minimum.
    result = model_input

    for hindi, english in sorted(
        HINDI_PLACE_NAMES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):

        result = result.replace(
            hindi,
            english,
        )

    print(
        "[NativeLanguage] "
        "FINAL FALLBACK:",
        result,
    )

    print(
        "========================================\n"
    )

    return result


# ============================================================
# ENGLISH -> HINDI
# ============================================================

def translate_english_to_hindi(text):

    if not text or not str(text).strip():

        return ""

    original_text = normalize_text(
        text
    )

    print(
        "\n========================================"
    )

    print(
        "[NativeLanguage] "
        "ENGLISH -> HINDI"
    )

    print(
        "[NativeLanguage] ORIGINAL:",
        original_text,
    )

    # ========================================================
    # HF
    # ========================================================

    translated = _huggingface_translate(
        original_text,
        EN_HI_MODEL,
    )

    if translated:

        print(
            "[NativeLanguage] "
            "HF FINAL RESULT:",
            translated,
        )

        print(
            "========================================\n"
        )

        return translated

    # ========================================================
    # FALLBACK
    # ========================================================

    normalized = (
        normalize_text(
            original_text
        )
        .lower()
    )

    if normalized in COMMON_ENGLISH_FALLBACKS:

        return COMMON_ENGLISH_FALLBACKS[
            normalized
        ]

    return original_text


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