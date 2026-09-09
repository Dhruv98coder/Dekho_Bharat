import os
import re
from urllib.parse import quote

import pandas as pd

from .intent import detect_intent


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

DATASET_PATH = os.path.join(
    PROJECT_DIR,
    "dataset",
    "GoPlan_Delhi_Places_AI_Dataset_READABLE(final).csv"
)


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
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )


# =========================================================

# SAFE VALUE

# HELPER

# =========================================================

def clean_value(value):

    if value is None:
        return ""

    if pd.isna(value):
        return ""

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

        # Full name
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

        # Short name before brackets
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
# PLACE → JSON FRIENDLY DATA
# =========================================================

def place_to_dict(place):

    if place is None:
        return None

    images = []

    for i in range(1, 6):

        column = f"image_{i}_url"

        if column in df.columns:

            image = clean_value(
                place.get(column, "")
            )

            if image:
                images.append(image)

    latitude = clean_value(
        place.get("latitude", "")
    )

    longitude = clean_value(
        place.get("longitude", "")
    )

    route_url = clean_value(
        place.get("route_google_maps_url", "")
    )

    # If dataset route URL is missing,
    # create a Google Maps destination URL.
    if not route_url and latitude and longitude:

        route_url = (
            "https://www.google.com/maps/dir/?api=1"
            f"&destination={latitude},{longitude}"
        )

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

    name = clean_value(place["place_name"])


    # ABOUT
    if intent == "ABOUT_PLACE":

        return (
            f"### About {name}\n\n"
            f"{clean_value(place.get('description', ''))}"
        )


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
            return (
                f"### History of {name}\n\n"
                "Historical information is currently unavailable."
            )

        return (
            f"### History of {name}\n\n"
            f"{history}"
        )


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
            answer += (
                f"🇮🇳 **Indian visitors:** {indian}\n"
            )

        if foreigner:
            answer += (
                f"🌍 **Foreign visitors:** {foreigner}\n"
            )

        if not indian and not foreigner:

            answer += (
                "Entry fee information is currently unavailable."
            )

        return answer


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
            answer += (
                f"📅 **Recommended period:** {season}\n"
            )

        if suggestion:
            answer += (
                f"💡 **Tip:** {suggestion}"
            )

        return answer


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
        )

        return (
            f"### How to Reach {name}\n\n"
            f"📍 **Location:** {location}\n"
            f"📌 **Coordinates:** {latitude}, {longitude}\n\n"
            "Your destination is ready for the "
            "Intelligent Route Agent."
        )


    # AWARENESS
    elif intent == "AWARENESS":

        tips = clean_value(
            place.get("awareness_tips", "")
        )

        return (
            f"### Things to Know Before Visiting {name}\n\n"
            f"{tips}"
        )


    # DURATION
    elif intent == "DURATION":

        duration = clean_value(
            place.get("recommended_duration", "")
        )

        return (
            f"### Recommended Duration for {name}\n\n"
            f"Plan approximately **{duration}** "
            "for this destination."
        )


    # NEARBY
    elif intent == "NEARBY":

        return (
            f"### Places Near {name}\n\n"
            "Nearby destinations can be calculated "
            "using this place's coordinates."
        )


    # UNKNOWN
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

    intent_result = detect_intent(question)

    intent = intent_result["intent"]

    place = find_place(question)

    # Use previous place
    if place is None:
        place = conversation_memory["current_place"]

    # Remember place
    if place is not None:
        conversation_memory["current_place"] = place

    answer = get_answer(
        place,
        intent
    )

    return {

        "success": True,

        "question": question,

        "intent": intent,

        "confidence": intent_result["confidence"],

        "matched_words": intent_result["matched_words"],

        "place": (
            place["place_name"]
            if place is not None
            else None
        ),

        "answer": answer,

        "place_data": place_to_dict(place)
    }


# =========================================================
# ALL 81 PLACES
# =========================================================

def get_all_places():

    places = []

    for _, row in df.iterrows():

        data = place_to_dict(row)

        if data:
            places.append(data)

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
