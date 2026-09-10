"""Small, portable place recommender for the GoPlane dataset.

The original version used a Windows-only absolute path and loaded a large
embedding model during Django import. This version keeps the same public
function, uses all CSV rows, and works from any machine without an extra
ML download. A lightweight lexical score is a better fit for this small
local dataset and makes the frontend available immediately.
"""

import csv
import re
from functools import lru_cache
from pathlib import Path


# ============================================================
# DATASET PATH
# ============================================================
# CSV location:
#
# GoPlan_GitHub_Ready_Integrated/
# └── goplan_home/
#     ├── engine.py
#     └── data/
#         └── Delhi_tourism_80_place_with_local_images.csv
#
# IMPORTANT:
# Do NOT use a hard-coded Windows path such as:
# D:\GoPlan_GitHub_Ready_Integrated\data\...
#
# This relative path works after moving/cloning the project.
DATASET_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "Delhi_tourism_80_place_with_local_images.csv"
)


# ============================================================
# DATASET COLUMNS
# ============================================================
IMAGE_COLUMNS = (
    "image_1",
    "image_2",
    "image_3",
    "image_4",
    "image_5",
)

TEXT_COLUMNS = (
    "name",
    "broad_category",
    "category",
    "description",
    "history",
    "famous_view",
    "location",
    "best_time",
)


# ============================================================
# STOP WORDS
# ============================================================
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "place",
    "places",
    "visit",
}


# ============================================================
# BASIC HELPERS
# ============================================================
def _clean(value):
    return str(value or "").strip()


def _number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _image_url(value):
    value = _clean(value)

    if not value or value.lower() == "nan":
        return ""

    # Keep external URLs and already-rooted Django paths unchanged.
    if value.startswith(("http://", "https://", "/")):
        return value

    # Dataset local image example:
    # images/red-fort/image.jpg
    #
    # Django static URL:
    # /static/images/red-fort/image.jpg
    return "/static/" + value.lstrip("/")


# ============================================================
# SERIALIZE DATASET ROW
# ============================================================
def _serialize(row, score=0.0):
    images = [
        _image_url(row.get(column))
        for column in IMAGE_COLUMNS
    ]

    images = [
        image
        for image in images
        if image
    ]

    rating = _number(row.get("rating"))

    return {
        "name": _clean(row.get("name")),
        "broad_category": _clean(row.get("broad_category")),
        "category": _clean(row.get("category")),
        "description": _clean(row.get("description")),
        "history": _clean(row.get("history")),
        "famous_view": _clean(row.get("famous_view")),
        "location": _clean(row.get("location")),
        "best_time": _clean(row.get("best_time")) or "Year round",
        "entry_fee": _clean(row.get("entry_fee")),
        "rating": rating,
        "latitude": _clean(row.get("latitude")),
        "longitude": _clean(row.get("longitude")),
        "images": images,
        "score": round(float(score), 4),
    }


# ============================================================
# LOAD DATASET
# ============================================================
@lru_cache(maxsize=1)
def _load_rows():
    """Load all valid place rows from the local CSV dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            "\nGoPlan dataset not found.\n\n"
            f"Expected file:\n{DATASET_PATH}\n\n"
            "Make sure the CSV exists at:\n"
            "goplan_home/data/"
            "Delhi_tourism_80_place_with_local_images.csv"
        )

    rows = []

    with DATASET_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as dataset:

        reader = csv.DictReader(dataset)

        for row in reader:
            if _clean(row.get("name")):
                rows.append(row)

    return rows


# ============================================================
# TOKENIZATION
# ============================================================
def _tokens(text):
    return {
        token
        for token in re.findall(
            r"[a-z0-9]+",
            _clean(text).lower(),
        )
        if token not in STOP_WORDS
        and len(token) > 1
    }


def _search_text(row):
    return " ".join(
        _clean(row.get(column))
        for column in TEXT_COLUMNS
    )


# ============================================================
# RECOMMENDATION SCORE
# ============================================================
def _lexical_score(query, row):
    query_tokens = _tokens(query)

    if not query_tokens:
        return 0.0

    name_tokens = _tokens(
        row.get("name")
    )

    category_tokens = _tokens(
        f"{row.get('broad_category')} "
        f"{row.get('category')}"
    )

    all_tokens = _tokens(
        _search_text(row)
    )

    matched = (
        len(query_tokens & all_tokens)
        / len(query_tokens)
    )

    name_bonus = (
        len(query_tokens & name_tokens)
        / len(query_tokens)
        * 0.35
    )

    category_bonus = (
        len(query_tokens & category_tokens)
        / len(query_tokens)
        * 0.18
    )

    rating_bonus = (
        _number(row.get("rating"))
        / 100
    )

    return min(
        1.0,
        matched * 0.47
        + name_bonus
        + category_bonus
        + rating_bonus,
    )


# ============================================================
# POPULAR PLACES
# ============================================================
def get_popular_places(top_k=8):
    """Return the highest-rated places from the supplied dataset."""

    rows = sorted(
        _load_rows(),
        key=lambda row: (
            _number(row.get("rating")),
            _clean(row.get("name")),
        ),
        reverse=True,
    )

    return [
        _serialize(row)
        for row in rows[:top_k]
    ]


# ============================================================
# TOTAL PLACES
# ============================================================
def get_total_places():
    return len(_load_rows())


# ============================================================
# GET ONE EXACT PLACE
# ============================================================
def get_place(name):
    """Return one dataset place by its exact display name."""

    wanted = _clean(name).casefold()

    if not wanted:
        return None

    for row in _load_rows():
        if _clean(row.get("name")).casefold() == wanted:
            return _serialize(row)

    return None


# ============================================================
# RECOMMEND PLACES
# ============================================================
def recommend_places(query, top_k=5):
    """Recommend places using lightweight lexical matching."""

    query = _clean(query)

    if not query:
        return []

    ranked = sorted(
        (
            (
                _lexical_score(query, row),
                index,
                row,
            )
            for index, row in enumerate(_load_rows())
        ),
        key=lambda item: (
            item[0],
            _number(item[2].get("rating")),
        ),
        reverse=True,
    )

    return [
        _serialize(row, score)
        for score, _, row in ranked[:top_k]
    ]