# chatbot/intent.py


INTENTS = {
    

    "HISTORY": [
        "history",
        "historical",
        "past",
        "built",
        "when was it built",
        "who built",
        "origin"
    ],

    "ENTRY_FEE": [
        "entry fee",
        "ticket price",
        "ticket",
        "fee",
        "price",
        "cost",
        "how much"
    ],

    "BEST_TIME": [
        "best time",
        "when should i visit",
        "when to visit",
        "best season",
        "good time to visit",
        "visiting time"
    ],

    "ROUTE": [
        "how to reach",
        "how can i reach",
        "how do i reach",
        "route",
        "directions",
        "how to go",
        "way to reach",
        "get there"
    ],

    "NEARBY": [
        "nearby",
        "near me",
        "near this place",
        "places nearby",
        "places around",
        "what is nearby"
    ],

    "ABOUT_PLACE": [
    "tell me about",
    "about this place",
    "what is this place",
    "why is it famous",
    "why is this famous",
    "why is red fort famous",
    "what is special",
    "what is special about",
    "what makes it famous",
    "what makes it important",
    "famous for",
    "information about",
    "describe this place"
],

    "DURATION": [
        "how long",
        "how much time",
        "time required",
        "time needed",
        "duration",
        "how many hours"
    ],

    "AWARENESS": [
        "tips",
        "things to know",
        "what should i know",
        "safety",
        "precautions",
        "rules",
        "be careful"
    ],

    "RECOMMENDATION": [
        "recommend",
        "recommendation",
        "suggest a place",
        "suggest places",
        "where should i go",
        "best places",
        "places to visit"
    ]
}


def normalize_text(text):
    """
    Convert user question into a simple normalized form.
    """

    return " ".join(text.lower().strip().split())


def detect_intent(text):
    """
    Detect the user's intention.
    """

    text = normalize_text(text)

    best_intent = "UNKNOWN"
    best_score = 0
    matched_words = []

    for intent, keywords in INTENTS.items():

        score = 0
        matches = []

        for keyword in keywords:

            if keyword in text:
                score += 1
                matches.append(keyword)

        if score > best_score:
            best_score = score
            best_intent = intent
            matched_words = matches

    if best_score == 0:

        return {
            "intent": "UNKNOWN",
            "confidence": 0,
            "matched_words": []
        }

    confidence = min(best_score * 50, 100)

    return {
        "intent": best_intent,
        "confidence": confidence,
        "matched_words": matched_words
    }


if __name__ == "__main__":

    questions = [

        "Tell me the history of Red Fort",

        "What is the entry fee?",

        "When should I visit this place?",

        "How can I reach Red Fort?",

        "What places are nearby?",

        "Why is this place famous?",

        "How much time do I need?",

        "Give me some safety tips",

        "Suggest some places to visit"

    ]

    for question in questions:

        result = detect_intent(question)

        print("\nQuestion:", question)
        print("Intent:", result["intent"])
        print("Confidence:", result["confidence"])
        print("Matched:", result["matched_words"])