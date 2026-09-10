import re


# ============================================================
# LANGUAGE DETECTION MODEL
# ============================================================

MODEL_NAME = "pruthwik/ilid-muril-model"

classifier = None


def _get_classifier():
    global classifier

    if classifier is None:
        from transformers import pipeline

        print("Loading language detection model...")

        classifier = pipeline(
            "text-classification",
            model=MODEL_NAME
        )

        print("Language detection model loaded.")

    return classifier


# ============================================================
# LIGHTWEIGHT INDIAN-SCRIPT DETECTION
# ============================================================
# Avoid loading another transformer model just to identify a
# script. This keeps the native-language endpoint stable on
# memory-limited production instances.
SCRIPT_RANGES = {
    "Bengali": r"[\u0980-\u09FF]",
    "Punjabi": r"[\u0A00-\u0A7F]",
    "Gujarati": r"[\u0A80-\u0AFF]",
    "Odia": r"[\u0B00-\u0B7F]",
    "Tamil": r"[\u0B80-\u0BFF]",
    "Telugu": r"[\u0C00-\u0C7F]",
    "Kannada": r"[\u0C80-\u0CFF]",
    "Malayalam": r"[\u0D00-\u0D7F]",
}

# ============================================================
# LANGUAGE LABEL MAPPING
# ============================================================

LANGUAGE_MAP = {
    "hi": "Hindi",
    "en": "English",

    "Hindi": "Hindi",
    "English": "English",

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

    # --------------------------------------------------------
    # Greetings
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Pronouns
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Demonstratives
    # --------------------------------------------------------

    "yeh",
    "ye",
    "woh",
    "wo",
    "isko",
    "usko",
    "yahan",
    "wahan",

    # --------------------------------------------------------
    # Questions
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Verbs
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Common words
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Travel
    # --------------------------------------------------------

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
    "place",
    "places",
    "dekho",
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

    # --------------------------------------------------------
    # Greetings
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Pronouns
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Demonstratives
    # --------------------------------------------------------

    "yeh": "यह",
    "ye": "यह",

    "woh": "वह",
    "wo": "वह",

    "isko": "इसको",
    "usko": "उसको",

    "yahan": "यहाँ",
    "wahan": "वहाँ",

    # --------------------------------------------------------
    # Questions
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Verbs
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Common words
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Travel
    # --------------------------------------------------------

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
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ============================================================
# DEVANAGARI DETECTION
# ============================================================

def contains_devanagari(text):

    if not text:
        return False

    return bool(
        re.search(
            r"[\u0900-\u097F]",
            text
        )
    )


def detect_indian_script(text):
    """Return a lightweight script-based Indian language guess."""
    if not text:
        return None
    for language, pattern in SCRIPT_RANGES.items():
        if re.search(pattern, text):
            return language
    return None


# ============================================================
# ROMAN HINDI DETECTION
# ============================================================

def detect_roman_hindi(text):

    text = normalize_text(text)

    if not text:

        return {
            "is_roman_hindi": False,
            "confidence": 0.0
        }


    # Do not classify mixed/native-script text as
    # Roman Hindi.
    if contains_devanagari(text):

        return {
            "is_roman_hindi": False,
            "confidence": 0.0
        }


    words = re.findall(
        r"[a-zA-Z]+",
        text.lower()
    )


    if not words:

        return {
            "is_roman_hindi": False,
            "confidence": 0.0
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


    # --------------------------------------------------------
    # Strong Roman Hindi
    # --------------------------------------------------------

    if strong_matches >= 1:

        return {
            "is_roman_hindi": True,
            "confidence": 90.0
        }


    # --------------------------------------------------------
    # Multiple Hindi words
    # --------------------------------------------------------

    if hindi_matches >= 2:

        ratio = (
            hindi_matches /
            len(words)
        )


        confidence = min(
            98.0,
            70.0 + (ratio * 28.0)
        )


        return {
            "is_roman_hindi": True,
            "confidence": round(
                confidence,
                2
            )
        }


    # --------------------------------------------------------
    # Short sentence
    # --------------------------------------------------------

    if (
        hindi_matches >= 1
        and
        len(words) <= 5
    ):

        return {
            "is_roman_hindi": True,
            "confidence": 80.0
        }


    return {
        "is_roman_hindi": False,
        "confidence": 0.0
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

        # ----------------------------------------------------
        # Keep punctuation
        # ----------------------------------------------------

        match = re.match(
            r"^([^a-zA-Z]*)([a-zA-Z]+)([^a-zA-Z]*)$",
            word
        )


        if not match:

            converted_words.append(
                word
            )

            continue


        prefix = match.group(1)
        core = match.group(2)
        suffix = match.group(3)


        lower_word = core.lower()


        # ----------------------------------------------------
        # Convert known Roman Hindi words
        # ----------------------------------------------------

        if lower_word in ROMAN_TO_DEVANAGARI:

            converted = ROMAN_TO_DEVANAGARI[
                lower_word
            ]

        else:

            # Unknown English words,
            # names and place names stay unchanged.
            converted = core


        converted_words.append(
            prefix +
            converted +
            suffix
        )


    return " ".join(
        converted_words
    )


# ============================================================
# IMPORTANT PLACE NAMES
# ============================================================

PLACE_NAMES = [

    "Qutub Minar",
    "Qutb Minar",
    "Qutub",
    "Qutb",

    "Red Fort",
    "Lal Qila",

    "India Gate",

    "Taj Mahal",

    "Agra Fort",

    "Humayun's Tomb",
    "Humayuns Tomb",

    "Lotus Temple",

    "Akshardham Temple",

    "Jama Masjid",

    "Jantar Mantar",

    "Purana Qila",

    "Safdarjung Tomb",

    "Connaught Place",

    "Rashtrapati Bhavan",

    "Parliament House",

    "Gateway of India",

    "Victoria Memorial",

    "Delhi",

    "Agra",
]


# ============================================================
# PROTECT PLACE NAMES
# ============================================================

def protect_place_names(text):

    protected = {}

    result = text


    # Longest names first.
    sorted_places = sorted(
        PLACE_NAMES,
        key=len,
        reverse=True
    )


    for index, place in enumerate(
        sorted_places
    ):

        pattern = re.compile(
            re.escape(place),
            re.IGNORECASE
        )


        if pattern.search(result):

            token = f"ZZPLACE{index}ZZ"


            protected[token] = place


            result = pattern.sub(
                token,
                result
            )


    return (
        result,
        protected
    )


# ============================================================
# RESTORE PLACE NAMES
# ============================================================

def restore_place_names(
    text,
    protected
):

    result = text


    if not protected:
        return result


    for token, place in protected.items():

        result = result.replace(
            token,
            place
        )


        result = result.replace(
            token.lower(),
            place
        )


        result = result.replace(
            token.upper(),
            place
        )


    return result


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
            "roman_hindi": False
        }


    # ========================================================
    # OTHER INDIAN SCRIPTS (NO LARGE MODEL)
    # ========================================================

    script_language = detect_indian_script(text)

    if script_language:
        return {
            "language": script_language,
            "language_code": script_language.lower(),
            "label": script_language.lower(),
            "confidence": 99.0,
            "roman_hindi": False
        }

    # ========================================================
    # ROMAN HINDI FIRST
    # ========================================================

    roman_result = detect_roman_hindi(
        text
    )


    if roman_result[
        "is_roman_hindi"
    ]:

        return {

            "language": "Hindi",

            "language_code": "hi",

            "label": "hi",

            "confidence":
                roman_result[
                    "confidence"
                ],

            "roman_hindi": True
        }


    # ========================================================
    # DEVANAGARI
    # ========================================================

    if contains_devanagari(
        text
    ):

        return {

            "language": "Hindi",

            "language_code": "hi",

            "label": "hi",

            "confidence": 99.0,

            "roman_hindi": False
        }


    # ========================================================
    # ENGLISH HEURISTIC
    # ========================================================

    english_words = {

        "the",
        "is",
        "are",
        "am",
        "my",
        "your",
        "you",
        "what",
        "where",
        "when",
        "how",
        "why",
        "this",
        "that",
        "these",
        "those",
        "and",
        "or",
        "to",
        "in",
        "of",
        "for",
        "with",
        "from",
        "please",
        "show",
        "tell",
        "give",
        "find",
        "place",
        "places",
        "want",
        "visit",
        "travel",
        "beautiful",
        "near",
        "best",
        "good",
        "looking",
    }


    words = re.findall(
        r"[a-zA-Z]+",
        text.lower()
    )


    english_matches = sum(
        1
        for word in words
        if word in english_words
    )


    if english_matches >= 1:

        ratio = (
            english_matches /
            len(words)
        )


        return {

            "language": "English",

            "language_code": "en",

            "label": "en",

            "confidence": round(
                min(
                    98.0,
                    70.0 + ratio * 25.0
                ),
                2
            ),

            "roman_hindi": False
        }


    # ========================================================
    # SAFE FALLBACK
    # ========================================================
    # No heavyweight fallback model. Unknown text is reported
    # cleanly instead of risking a worker crash / 502.
    return {
        "language": "Unknown",
        "language_code": "unknown",
        "label": "unknown",
        "confidence": 0.0,
        "roman_hindi": False
    }
