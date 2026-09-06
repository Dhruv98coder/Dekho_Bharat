import torch
import re


# ============================================================
# MODELS
# ============================================================

HI_EN_MODEL = "Helsinki-NLP/opus-mt-hi-en"
EN_HI_MODEL = "Helsinki-NLP/opus-mt-en-hi"


hi_en_tokenizer = None
hi_en_model = None
en_hi_tokenizer = None
en_hi_model = None

def _get_hi_en():
    global hi_en_tokenizer, hi_en_model
    if hi_en_tokenizer is None or hi_en_model is None:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        hi_en_tokenizer = AutoTokenizer.from_pretrained(HI_EN_MODEL)
        hi_en_model = AutoModelForSeq2SeqLM.from_pretrained(HI_EN_MODEL)
    return hi_en_tokenizer, hi_en_model

def _get_en_hi():
    global en_hi_tokenizer, en_hi_model
    if en_hi_tokenizer is None or en_hi_model is None:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        en_hi_tokenizer = AutoTokenizer.from_pretrained(EN_HI_MODEL)
        en_hi_model = AutoModelForSeq2SeqLM.from_pretrained(EN_HI_MODEL)
    return en_hi_tokenizer, en_hi_model


# ============================================================
# HINDI PLACE NAMES
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
# CORRECT ENGLISH PLACE NAMES
# ============================================================

def correct_english_place_names(text):

    if not text:
        return text

    corrections = sorted(
        ENGLISH_PLACE_CORRECTIONS.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for wrong, correct in corrections:

        text = re.sub(
            re.escape(wrong),
            correct,
            text,
            flags=re.IGNORECASE
        )

    return text.strip()


# ============================================================
# SPECIAL HINDI → ENGLISH SENTENCES
# ============================================================

def translate_known_hindi_sentence(text):

    text = text.strip()

    # --------------------------------------------------------
    # मैं <PLACE> देखने जा रहा हूं
    # --------------------------------------------------------

    for hindi_place, english_place in HINDI_PLACE_NAMES.items():

        patterns = [

            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जा\s+रहा\s+हूं$",
            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जा\s+रहा\s+हूँ$",

        ]

        for pattern in patterns:

            if re.match(pattern, text):

                return f"I am going to see {english_place}."


    # --------------------------------------------------------
    # मैं <PLACE> देखने जाऊंगा
    # --------------------------------------------------------

    for hindi_place, english_place in HINDI_PLACE_NAMES.items():

        patterns = [

            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊंगा$",
            rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊँगा$",

        ]

        for pattern in patterns:

            if re.match(pattern, text):

                return f"I will go to see {english_place}."


    # --------------------------------------------------------
    # आज मैं <PLACE> देखने जाऊंगा
    # --------------------------------------------------------

    for hindi_place, english_place in HINDI_PLACE_NAMES.items():

        patterns = [

            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊंगा$",
            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊँगा$",

        ]

        for pattern in patterns:

            if re.match(pattern, text):

                return f"Today I will go to see {english_place}."


    # --------------------------------------------------------
    # आज मैं <PLACE> देखने जाऊंगा कल etc.
    # --------------------------------------------------------

    for hindi_place, english_place in HINDI_PLACE_NAMES.items():

        pattern = rf"^मैं\s+{re.escape(hindi_place)}\s+देखने\s+जाऊंगा\s+कल$"

        if re.match(pattern, text):

            return f"I will go to see {english_place} tomorrow."


    # --------------------------------------------------------
    # आज मैं <PLACE> जाऊंगा
    # --------------------------------------------------------

    for hindi_place, english_place in HINDI_PLACE_NAMES.items():

        patterns = [

            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+जाऊंगा$",
            rf"^आज\s+मैं\s+{re.escape(hindi_place)}\s+जाऊँगा$",

        ]

        for pattern in patterns:

            if re.match(pattern, text):

                return f"Today I will go to {english_place}."


    return None


# ============================================================
# HINDI → ENGLISH
# ============================================================

def translate_hindi_to_english(text):
    global hi_en_tokenizer, hi_en_model
    hi_en_tokenizer, hi_en_model = _get_hi_en()

    if not text or not text.strip():
        return ""

    text = text.strip()


    # ========================================================
    # STEP 1
    # KNOWN SENTENCE PATTERNS
    # ========================================================

    known_translation = translate_known_hindi_sentence(text)

    if known_translation:

        return known_translation


    # ========================================================
    # STEP 2
    # HANDLE SENTENCES CONTAINING PLACE NAMES
    # ========================================================

    # Replace Hindi place names with their English names BEFORE
    # sending the sentence to the translation model.
    #
    # This prevents the model from translating:
    # कुतुब मीनार → Kuthble Tower
    #
    # or:
    # लाल किला → PALCHOLDER0

    translated_input = text

    places = sorted(
        HINDI_PLACE_NAMES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for hindi_place, english_place in places:

        translated_input = translated_input.replace(
            hindi_place,
            english_place
        )


    # ========================================================
    # STEP 3
    # TRANSLATE
    # ========================================================

    inputs = hi_en_tokenizer(
        translated_input,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )

    with torch.no_grad():

        output = hi_en_model.generate(
            **inputs,
            max_length=128,
            num_beams=8,
            do_sample=False,
            early_stopping=True
        )


    translated = hi_en_tokenizer.decode(
        output[0],
        skip_special_tokens=True
    )


    # ========================================================
    # STEP 4
    # CORRECT PLACE NAMES
    # ========================================================

    translated = correct_english_place_names(
        translated
    )


    return translated.strip()


# ============================================================
# ENGLISH → HINDI
# ============================================================

def translate_english_to_hindi(text):
    global en_hi_tokenizer, en_hi_model
    en_hi_tokenizer, en_hi_model = _get_en_hi()

    if not text or not text.strip():
        return ""

    text = text.strip()


    # ========================================================
    # TOKENIZE
    # ========================================================

    inputs = en_hi_tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )


    # ========================================================
    # TRANSLATE
    # ========================================================

    with torch.no_grad():

        output = en_hi_model.generate(
            **inputs,
            max_length=128,
            num_beams=5,
            do_sample=False,
            early_stopping=True
        )


    translated = en_hi_tokenizer.decode(
        output[0],
        skip_special_tokens=True
    )


    return translated.strip()


# ============================================================
# AUTO TRANSLATOR
# ============================================================

def auto_translate(text, detected_language):

    if not text or not text.strip():
        return ""

    text = text.strip()


    # ========================================================
    # HINDI → ENGLISH
    # ========================================================

    if detected_language == "Hindi":

        return translate_hindi_to_english(text)


    # ========================================================
    # ENGLISH → HINDI
    # ========================================================

    if detected_language == "English":

        return translate_english_to_hindi(text)


    # ========================================================
    # OTHER
    # ========================================================

    return text