import os
import re
<<<<<<< HEAD
from urllib.parse import quote

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
import pandas as pd

from .intent import detect_intent


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
<<<<<<< HEAD

DATASET_PATH = os.path.join(
    BASE_DIR,
=======
PROJECT_DIR = os.path.dirname(BASE_DIR)

DATASET_PATH = os.path.join(
    PROJECT_DIR,
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    "dataset",
    "GoPlan_Delhi_Places_AI_Dataset_READABLE(final).csv"
)

<<<<<<< HEAD
LOCAL_IMAGES_PATH = os.path.join(
    BASE_DIR,
    "static",
    "chatbot",
    "places"
)

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

# =========================================================
# LOAD DATASET
# =========================================================

df = pd.read_csv(
    DATASET_PATH,
    sep="\t",
    encoding="utf-8-sig",
    engine="python"
)


# =========================================================
# SAFE COLUMNS
# =========================================================

TEXT_COLUMNS = [
    "place_name",
    "broad_category",
    "category",
    "description",
    "history_30_lines",
    "famous_view",
    "location",
    "best_time_season",
    "best_time_suggestion",
    "entry_fee_indian",
    "entry_fee_foreigner",
    "entry_is_free",
    "rating",
    "recommended_duration",
    "suitable_for",
    "question_suggestions",
    "awareness_tips",
    "how_to_reach",
    "destination_address",
    "route_google_maps_url",
    "chatbot_place_key",
    "qa_history",
    "qa_description",
    "qa_entry_fee",
    "qa_best_time",
    "qa_location",
    "qa_rating",
    "chatbot_note",
    "image_1_url",
    "image_2_url",
    "image_3_url",
    "image_4_url",
    "image_5_url",
    "image_1_source_search",
    "image_2_source_search",
    "image_3_source_search",
    "image_4_source_search",
    "image_5_source_search",
    "source",
    "name",
    "history",
    "history_full",
    "best_time",
    "entry_fee",
    "route_destination_query",
]


for column in TEXT_COLUMNS:

    if column in df.columns:
<<<<<<< HEAD

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )


# =========================================================
<<<<<<< HEAD
# SAFE VALUE
=======
# HELPER
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
# =========================================================

def clean_value(value):

    if value is None:
        return ""

<<<<<<< HEAD
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
=======
    if pd.isna(value):
        return ""
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    return str(value).strip()


# =========================================================
# FIND PLACE
# =========================================================

def find_place(question):

    question = clean_value(question).lower()

    question_clean = re.sub(
        r"[^a-z0-9\s]",
        " ",
        question
    )

    question_clean = " ".join(
        question_clean.split()
    )

    places = sorted(
        df["place_name"]
        .dropna()
        .unique(),
        key=lambda x: len(str(x)),
        reverse=True
    )

    for place in places:

        original_name = clean_value(place)

        if not original_name:
            continue

        place_clean = original_name.lower()

<<<<<<< HEAD
        # -------------------------------------------------
        # FULL NAME
        # -------------------------------------------------

=======
        # Full name
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        place_normalized = re.sub(
            r"[^a-z0-9\s]",
            " ",
            place_clean
        )

        place_normalized = " ".join(
            place_normalized.split()
        )

        if place_normalized in question_clean:

            result = df[
                df["place_name"]
                .str.lower()
                .str.strip()
                == place_clean
            ]

            if not result.empty:
                return result.iloc[0]

<<<<<<< HEAD
        # -------------------------------------------------
        # SHORT NAME BEFORE BRACKETS
        # -------------------------------------------------

=======
        # Short name before brackets
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        short_name = place_clean.split("(")[0].strip()

        if len(short_name) >= 4:

            if re.search(
                r"\b" + re.escape(short_name) + r"\b",
                question_clean
            ):

                result = df[
                    df["place_name"]
                    .str.lower()
                    .str.strip()
                    == place_clean
                ]

                if not result.empty:
                    return result.iloc[0]

    return None


# =========================================================
<<<<<<< HEAD
# FIND LOCAL IMAGE DIRECTORY
# =========================================================

def get_local_image_directory(place_id):

    place_id = clean_value(place_id)

    if not place_id:
        return None

    # -----------------------------------------------------
    # EXAMPLE:
    #
    # DEL-001 -> 0
    # DEL-002 -> 1
    # DEL-003 -> 2
    #
    # If your folders are named directly as place_id,
    # that is also supported.
    # -----------------------------------------------------

    # First try exact place_id folder.
    exact_dir = os.path.join(
        LOCAL_IMAGES_PATH,
        place_id
    )

    if os.path.isdir(exact_dir):
        return exact_dir

    # -----------------------------------------------------
    # Extract numeric part from place_id
    # -----------------------------------------------------

    match = re.search(
        r"(\d+)$",
        place_id
    )

    if not match:
        return None

    place_number = int(
        match.group(1)
    )

    # DEL-001 -> folder 0
    numeric_folder = str(
        place_number - 1
    )

    numeric_dir = os.path.join(
        LOCAL_IMAGES_PATH,
        numeric_folder
    )

    if os.path.isdir(numeric_dir):
        return numeric_dir

    # -----------------------------------------------------
    # Fallback: try same number
    # Example DEL-001 -> 1
    # -----------------------------------------------------

    same_number_dir = os.path.join(
        LOCAL_IMAGES_PATH,
        str(place_number)
    )

    if os.path.isdir(same_number_dir):
        return same_number_dir

    return None


# =========================================================
# NATURAL SORT
# =========================================================

def natural_key(filename):

    matches = re.findall(
        r"\d+",
        filename
    )

    if matches:

        return (
            int(matches[0]),
            filename.lower()
        )

    return (
        999,
        filename.lower()
    )


# =========================================================
# LOAD LOCAL IMAGES
# =========================================================

def get_local_images(place_id):

    images = []

    image_dir = get_local_image_directory(
        place_id
    )

    if image_dir is None:
        return images

    try:

        filenames = sorted(
            os.listdir(image_dir),
            key=natural_key
        )

    except OSError:
        return images

    allowed_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".avif"
    )

    for filename in filenames:

        if not filename.lower().endswith(
            allowed_extensions
        ):
            continue

        file_path = os.path.join(
            image_dir,
            filename
        )

        if not os.path.isfile(file_path):
            continue

        folder_name = os.path.basename(
            image_dir
        )

        images.append(
            "/static/chatbot/places/"
            f"{quote(folder_name)}/"
            f"{quote(filename)}"
        )

    return images


# =========================================================
=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
# PLACE → JSON FRIENDLY DATA
# =========================================================

def place_to_dict(place):

    if place is None:
        return None

<<<<<<< HEAD
    # =====================================================
    # LOCAL IMAGES
    # =====================================================

    place_id = clean_value(
        place.get("place_id", "")
    )

    images = get_local_images(
        place_id
    )

    # =====================================================
    # COORDINATES
    # =====================================================
=======
    images = []

    for i in range(1, 6):

        column = f"image_{i}_url"

        if column in df.columns:

            image = clean_value(
                place.get(column, "")
            )

            if image:
                images.append(image)
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    latitude = clean_value(
        place.get("latitude", "")
    )

    longitude = clean_value(
        place.get("longitude", "")
    )

<<<<<<< HEAD
    # =====================================================
    # GOOGLE MAPS URL
    # =====================================================

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    route_url = clean_value(
        place.get("route_google_maps_url", "")
    )

    # If dataset route URL is missing,
    # create a Google Maps destination URL.
<<<<<<< HEAD

    if (
        not route_url
        and latitude
        and longitude
    ):
=======
    if not route_url and latitude and longitude:
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

        route_url = (
            "https://www.google.com/maps/dir/?api=1"
            f"&destination={latitude},{longitude}"
        )

<<<<<<< HEAD
    # =====================================================
    # RETURN DATA
    # =====================================================

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    return {

        "place_id": clean_value(
            place.get("place_id", "")
        ),

        "name": clean_value(
            place.get("place_name", "")
        ),

        "category": clean_value(
            place.get("category", "")
        ),

        "broad_category": clean_value(
            place.get("broad_category", "")
        ),

        "description": clean_value(
            place.get("description", "")
        ),

        "history": clean_value(
            place.get("history_30_lines", "")
        ),

        "famous_view": clean_value(
            place.get("famous_view", "")
        ),

        "location": clean_value(
            place.get("location", "")
        ),

        "address": clean_value(
            place.get("destination_address", "")
        ),

        "latitude": latitude,

        "longitude": longitude,

        "best_time_season": clean_value(
            place.get("best_time_season", "")
        ),

        "best_time_suggestion": clean_value(
            place.get("best_time_suggestion", "")
        ),

        "entry_fee_indian": clean_value(
            place.get("entry_fee_indian", "")
        ),

        "entry_fee_foreigner": clean_value(
            place.get("entry_fee_foreigner", "")
        ),

        "entry_is_free": clean_value(
            place.get("entry_is_free", "")
        ),

        "rating": clean_value(
            place.get("rating", "")
        ),

        "duration": clean_value(
            place.get("recommended_duration", "")
        ),

        "suitable_for": clean_value(
            place.get("suitable_for", "")
        ),

        "tips": clean_value(
            place.get("awareness_tips", "")
        ),

        "how_to_reach": clean_value(
            place.get("how_to_reach", "")
        ),

        "google_maps_url": route_url,

<<<<<<< HEAD
        # LOCAL IMAGES
=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        "images": images
    }


# =========================================================
# GET ANSWER
# =========================================================

def get_answer(place, intent):

    if place is None:

        return (
            "I couldn't identify the place you're asking about. "
            "Please mention the place name."
        )

<<<<<<< HEAD
    name = clean_value(
        place["place_name"]
    )

    # =====================================================
    # ABOUT
    # =====================================================

=======
    name = clean_value(place["place_name"])


    # ABOUT
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    if intent == "ABOUT_PLACE":

        return (
            f"### About {name}\n\n"
            f"{clean_value(place.get('description', ''))}"
        )

<<<<<<< HEAD
    # =====================================================
    # HISTORY
    # =====================================================

    elif intent == "HISTORY":

        history = clean_value(
            place.get(
                "history_30_lines",
                ""
            )
        )

        if not history:

            history = clean_value(
                place.get(
                    "history_full",
                    ""
                )
            )

        if not history:

            history = clean_value(
                place.get(
                    "history",
                    ""
                )
            )

        if not history:

=======

    # HISTORY
    elif intent == "HISTORY":

        history = clean_value(
            place.get("history_30_lines", "")
        )

        if not history:
            history = clean_value(
                place.get("history_full", "")
            )

        if not history:
            history = clean_value(
                place.get("history", "")
            )

        if not history:
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            return (
                f"### History of {name}\n\n"
                "Historical information is currently unavailable."
            )

        return (
            f"### History of {name}\n\n"
            f"{history}"
        )

<<<<<<< HEAD
    # =====================================================
    # ENTRY FEE
    # =====================================================

    elif intent == "ENTRY_FEE":

        indian = clean_value(
            place.get(
                "entry_fee_indian",
                ""
            )
        )

        foreigner = clean_value(
            place.get(
                "entry_fee_foreigner",
                ""
            )
        )

        answer = (
            f"### Entry Fee — {name}\n\n"
        )

        if indian:

=======

    # ENTRY FEE
    elif intent == "ENTRY_FEE":

        indian = clean_value(
            place.get("entry_fee_indian", "")
        )

        foreigner = clean_value(
            place.get("entry_fee_foreigner", "")
        )

        answer = f"### Entry Fee — {name}\n\n"

        if indian:
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            answer += (
                f"🇮🇳 **Indian visitors:** {indian}\n"
            )

        if foreigner:
<<<<<<< HEAD

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            answer += (
                f"🌍 **Foreign visitors:** {foreigner}\n"
            )

        if not indian and not foreigner:

            answer += (
                "Entry fee information is currently unavailable."
            )

        return answer

<<<<<<< HEAD
    # =====================================================
    # BEST TIME
    # =====================================================

    elif intent == "BEST_TIME":

        season = clean_value(
            place.get(
                "best_time_season",
                ""
            )
        )

        suggestion = clean_value(
            place.get(
                "best_time_suggestion",
                ""
            )
        )

        answer = (
            f"### Best Time to Visit {name}\n\n"
        )

        if season:

=======

    # BEST TIME
    elif intent == "BEST_TIME":

        season = clean_value(
            place.get("best_time_season", "")
        )

        suggestion = clean_value(
            place.get("best_time_suggestion", "")
        )

        answer = f"### Best Time to Visit {name}\n\n"

        if season:
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            answer += (
                f"📅 **Recommended period:** {season}\n"
            )

        if suggestion:
<<<<<<< HEAD

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            answer += (
                f"💡 **Tip:** {suggestion}"
            )

        return answer

<<<<<<< HEAD
    # =====================================================
    # ROUTE
    # =====================================================

    elif intent == "ROUTE":

        latitude = clean_value(
            place.get(
                "latitude",
                ""
            )
        )

        longitude = clean_value(
            place.get(
                "longitude",
                ""
            )
        )

        location = clean_value(
            place.get(
                "location",
                ""
            )
=======

    # ROUTE
    elif intent == "ROUTE":

        latitude = clean_value(
            place.get("latitude", "")
        )

        longitude = clean_value(
            place.get("longitude", "")
        )

        location = clean_value(
            place.get("location", "")
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        )

        return (
            f"### How to Reach {name}\n\n"
            f"📍 **Location:** {location}\n"
            f"📌 **Coordinates:** {latitude}, {longitude}\n\n"
            "Your destination is ready for the "
            "Intelligent Route Agent."
        )

<<<<<<< HEAD
    # =====================================================
    # AWARENESS
    # =====================================================

    elif intent == "AWARENESS":

        tips = clean_value(
            place.get(
                "awareness_tips",
                ""
            )
=======

    # AWARENESS
    elif intent == "AWARENESS":

        tips = clean_value(
            place.get("awareness_tips", "")
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        )

        return (
            f"### Things to Know Before Visiting {name}\n\n"
            f"{tips}"
        )

<<<<<<< HEAD
    # =====================================================
    # DURATION
    # =====================================================

    elif intent == "DURATION":

        duration = clean_value(
            place.get(
                "recommended_duration",
                ""
            )
=======

    # DURATION
    elif intent == "DURATION":

        duration = clean_value(
            place.get("recommended_duration", "")
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        )

        return (
            f"### Recommended Duration for {name}\n\n"
            f"Plan approximately **{duration}** "
            "for this destination."
        )

<<<<<<< HEAD
    # =====================================================
    # NEARBY
    # =====================================================

=======

    # NEARBY
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    elif intent == "NEARBY":

        return (
            f"### Places Near {name}\n\n"
            "Nearby destinations can be calculated "
            "using this place's coordinates."
        )

<<<<<<< HEAD
    # =====================================================
    # UNKNOWN
    # =====================================================

=======

    # UNKNOWN
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    return (
        f"I know about **{name}**.\n\n"
        "You can ask me about its **history**, "
        "**entry fee**, **best time**, **route**, "
        "**duration**, or **travel tips**."
    )


# =========================================================
# CHAT MEMORY
# =========================================================

conversation_memory = {
    "current_place": None
}


# =========================================================
# CHAT
# =========================================================

def chat(question):

<<<<<<< HEAD
    intent_result = detect_intent(
        question
    )

    intent = intent_result["intent"]

    place = find_place(
        question
    )

    # -----------------------------------------------------
    # USE PREVIOUS PLACE
    # -----------------------------------------------------

    if place is None:

        place = conversation_memory[
            "current_place"
        ]

    # -----------------------------------------------------
    # REMEMBER PLACE
    # -----------------------------------------------------

    if place is not None:

        conversation_memory[
            "current_place"
        ] = place

    # -----------------------------------------------------
    # ANSWER
    # -----------------------------------------------------
=======
    intent_result = detect_intent(question)

    intent = intent_result["intent"]

    place = find_place(question)

    # Use previous place
    if place is None:
        place = conversation_memory["current_place"]

    # Remember place
    if place is not None:
        conversation_memory["current_place"] = place
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    answer = get_answer(
        place,
        intent
    )

<<<<<<< HEAD
    # -----------------------------------------------------
    # PLACE DATA
    # -----------------------------------------------------

    place_data = place_to_dict(
        place
    )

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    return {

        "success": True,

        "question": question,

        "intent": intent,

<<<<<<< HEAD
        "confidence": intent_result[
            "confidence"
        ],

        "matched_words": intent_result[
            "matched_words"
        ],
=======
        "confidence": intent_result["confidence"],

        "matched_words": intent_result["matched_words"],
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

        "place": (
            place["place_name"]
            if place is not None
            else None
        ),

        "answer": answer,

<<<<<<< HEAD
        "place_data": place_data
=======
        "place_data": place_to_dict(place)
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    }


# =========================================================
<<<<<<< HEAD
# ALL PLACES
=======
# ALL 81 PLACES
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
# =========================================================

def get_all_places():

    places = []

    for _, row in df.iterrows():

<<<<<<< HEAD
        data = place_to_dict(
            row
        )

        if data:

            places.append(
                data
            )
=======
        data = place_to_dict(row)

        if data:
            places.append(data)
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    return places


# =========================================================
# GET PLACE BY NAME
# =========================================================

def get_place_by_name(place_name):

    if not place_name:
        return None

    target = clean_value(
        place_name
    ).lower()

    result = df[
        df["place_name"]
        .str.lower()
        .str.strip()
        == target
    ]

    if result.empty:
        return None

    return place_to_dict(
        result.iloc[0]
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    questions = [

        "Tell me about Red Fort",

        "What is the entry fee?",

        "When should I visit?",

        "How can I reach there?",

        "Tell me the history",

        "Give me some tips"

    ]

    for question in questions:

<<<<<<< HEAD
        print(
            "\n" + "=" * 60
        )

        result = chat(
            question
        )

        print(
            "QUESTION:"
        )

        print(
            result["question"]
        )

        print(
            "\nPLACE:"
        )

        print(
            result["place"]
        )

        print(
            "\nINTENT:"
        )

        print(
            result["intent"]
        )

        print(
            "\nANSWER:"
        )

        print(
            result["answer"]
        )

        print(
            "\nIMAGES:"
        )

        if result["place_data"]:

            print(
                len(
                    result[
                        "place_data"
                    ][
                        "images"
                    ]
                )
            )

            print(
                result[
                    "place_data"
                ][
                    "images"
                ]
            )

        else:

            print(0)
=======
        print("\n" + "=" * 60)

        result = chat(question)

        print("QUESTION:")
        print(result["question"])

        print("\nPLACE:")
        print(result["place"])

        print("\nINTENT:")
        print(result["intent"])

        print("\nANSWER:")
        print(result["answer"])

        print("\nIMAGES:")
        print(
            len(
                result["place_data"]["images"]
            )
            if result["place_data"]
            else 0
        )
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
