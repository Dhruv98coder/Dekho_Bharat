import os
import re
from urllib.parse import quote

import pandas as pd

from .intent import detect_intent


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "GoPlan_Delhi_Places_AI_Dataset_READABLE(final).csv"
)

LOCAL_IMAGES_PATH = os.path.join(
    BASE_DIR,
    "static",
    "chatbot",
    "places",
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
# HELPER
# =========================================================

def clean_value(value):

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

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
    place_id = clean_value(place.get("place_id", ""))

    # Bundled images are stored in numeric folders:
    # DEL-001 -> 0, DEL-002 -> 1, ... DEL-081 -> 80.
    match = re.search(r"(\d+)$", place_id)
    image_folder = str(max(int(match.group(1)) - 1, 0)) if match else ""
    image_dir = (
        os.path.join(LOCAL_IMAGES_PATH, image_folder)
        if image_folder else ""
    )

    # Backward-compatible fallback for a direct place_id folder.
    if not os.path.isdir(image_dir) and place_id:
        direct_dir = os.path.join(LOCAL_IMAGES_PATH, place_id)
        if os.path.isdir(direct_dir):
            image_dir = direct_dir

    if os.path.isdir(image_dir):
        def natural_key(filename):
            match = re.search(r"(\d+)", filename)
            return (int(match.group(1)) if match else 999, filename.lower())

        for filename in sorted(os.listdir(image_dir), key=natural_key):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".avif")):
                images.append(
                    f"/static/chatbot/places/{quote(os.path.basename(image_dir))}/{quote(filename)}"
                )

    # Keep the dataset URLs as a second source. This is important on Render:
    # if a collected/static file is missing, the browser can fall back to the
    # original image URL instead of showing a broken-image icon.
    remote_images = []
    for key in (
        "image_1_url",
        "image_2_url",
        "image_3_url",
        "image_4_url",
        "image_5_url",
    ):
        image_url = clean_value(place.get(key, ""))
        if image_url and image_url not in remote_images:
            remote_images.append(image_url)

    # If no bundled images exist, use remote images directly.
    if not images:
        images = list(remote_images)

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

        "images": images,

        # Browser fallback for deployments where a particular static image
        # was not collected by WhiteNoise/collectstatic.
        "remote_images": remote_images,
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

        route_url = clean_value(place.get("route_google_maps_url", ""))
        if not route_url and latitude and longitude:
            route_url = (
                "https://www.google.com/maps/dir/?api=1"
                f"&destination={latitude},{longitude}"
            )

        answer = (
            f"### How to Reach {name}\n\n"
            f"📍 **Location:** {location}\n"
            f"📌 **Coordinates:** {latitude}, {longitude}\n"
        )
        if route_url:
            answer += f"\n🗺️ **Google Maps:** {route_url}"
        else:
            answer += "\nRoute information is currently unavailable."
        return answer


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


    # RECOMMENDATION
    elif intent == "RECOMMENDATION":
        category = clean_value(place.get("category", ""))
        broad_category = clean_value(place.get("broad_category", ""))
        return (
            "### Recommendation\n\n"
            f"**{name}** is a {category or broad_category or 'destination'} "
            "in Delhi. Ask for a specific category or preference to get "
            "better recommendations."
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
