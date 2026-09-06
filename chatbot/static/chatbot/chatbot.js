/* =========================================================
   DEKHOCHAT
   GoPlan AI Travel Assistant
   CLEAN + FIXED VERSION
========================================================= */


/* =========================================================
   GLOBAL STATE
========================================================= */

let currentPlace = null;
let currentPlaceData = null;


/* =========================================================
   API URLS
   Django chatbot app is mounted at /shristi/
========================================================= */

const API = {
    places: "/shristi/places/",
    chat: "/shristi/api/"
};


/* =========================================================
   DEFAULT IMAGE
========================================================= */

const DEFAULT_PLACE_IMAGE =
    "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1000&q=85";


/* =========================================================
   PAGE INITIALIZATION
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("DekhoChat initialized.");

    loadAllPlaces();
    initializeSearch();

    window.addEventListener("resize", function () {

        if (window.innerWidth > 900) {
            closeAllSidebars();
        }

    });

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {
            closeAllSidebars();
        }

    });

});


/* =========================================================
   LOAD ALL PLACES
   Django -> /shristi/places/
========================================================= */

async function loadAllPlaces() {

    const selector =
        document.getElementById("place-selector");

    const grid =
        document.getElementById("explore-grid");


    try {

        console.log("Loading destinations...");


        const response =
            await fetch(API.places, {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            });


        if (!response.ok) {

            throw new Error(
                `Places API returned ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "PLACES API RESPONSE:",
            data
        );


        if (!data.success) {

            throw new Error(
                data.error ||
                "Could not load places."
            );

        }


        const places =
            Array.isArray(data.places)
                ? data.places
                : [];


        console.log(
            `Loaded ${places.length} places.`
        );


        populatePlaceDropdown(
            selector,
            places
        );


        populatePlaceGrid(
            grid,
            places
        );


    } catch (error) {

        console.error(
            "LOAD PLACES ERROR:",
            error
        );


        showPlaceLoadError(
            grid,
            error
        );

    }

}


/* =========================================================
   POPULATE PLACE DROPDOWN
========================================================= */

function populatePlaceDropdown(
    selector,
    places
) {

    if (!selector) {
        return;
    }


    selector.innerHTML = "";


    const defaultOption =
        document.createElement("option");


    defaultOption.value = "";


    defaultOption.textContent =
        `Select a place from ${places.length || 81} destinations...`;


    selector.appendChild(
        defaultOption
    );


    places.forEach(function (place) {

        const option =
            document.createElement("option");


        option.value =
            place.name || "";


        option.textContent =
            place.name || "Unknown Place";


        selector.appendChild(
            option
        );

    });

}


/* =========================================================
   POPULATE PLACE GRID
========================================================= */

function populatePlaceGrid(
    grid,
    places
) {

    if (!grid) {
        return;
    }


    grid.innerHTML = "";


    places.forEach(function (place) {

        const card =
            createPlaceCard(place);


        grid.appendChild(
            card
        );

    });

}


/* =========================================================
   PLACE LOAD ERROR
========================================================= */

function showPlaceLoadError(
    grid,
    error
) {

    if (!grid) {
        return;
    }


    grid.innerHTML = `

        <div class="place-load-error">

            ⚠️ Unable to load destinations.

            <br>

            <small>
                ${escapeHTML(
                    error?.message ||
                    "Unknown error"
                )}
            </small>

        </div>

    `;

}


/* =========================================================
   CREATE PLACE CARD
========================================================= */

function createPlaceCard(place) {

    const article =
        document.createElement("article");


    article.className =
        "place-card";


    article.dataset.placeName =
        place.name || "";


    article.onclick = function () {

        selectPlace(
            place.name
        );

    };


    /* -----------------------------------------------------
       IMAGE
    ----------------------------------------------------- */

    let image = "";


    if (
        Array.isArray(place.images) &&
        place.images.length > 0
    ) {

        image =
            place.images.find(
                img =>
                    typeof img === "string" &&
                    img.trim() !== ""
            ) || "";

    }


    if (!image) {

        image =
            place.image_url ||
            place.image ||
            "";

    }


    if (!image) {

        image =
            DEFAULT_PLACE_IMAGE;

    }


    /* -----------------------------------------------------
       BASIC DATA
    ----------------------------------------------------- */

    const category =
        place.category ||
        place.broad_category ||
        "Destination";


    const location =
        place.location ||
        place.address ||
        "Delhi";


    const description =
        place.description ||
        "Explore this destination with DekhoChat.";


    const safeDescription =
        String(description);


    article.innerHTML = `

        <div class="place-image-wrapper">

            <img
                src="${escapeAttribute(image)}"
                alt="${escapeAttribute(
                    place.name || "Place"
                )}"
                loading="lazy"
                onerror="this.onerror=null;this.src='${DEFAULT_PLACE_IMAGE}'"
            >

            <span class="place-category">
                ${escapeHTML(category)}
            </span>

        </div>


        <div class="place-card-content">

            <h4>
                ${escapeHTML(
                    place.name || "Unknown Place"
                )}
            </h4>


            <p>
                ${escapeHTML(
                    safeDescription.substring(
                        0,
                        140
                    )
                )}
            </p>


            <div class="place-card-bottom">

                <span>

                    <i class="fa-solid fa-location-dot"></i>

                    ${escapeHTML(location)}

                </span>


                <span class="explore-arrow">

                    Explore

                    <i class="fa-solid fa-arrow-right"></i>

                </span>

            </div>

        </div>

    `;


    return article;

}


/* =========================================================
   SELECT PLACE
   Django -> /shristi/place/<place_name>/
========================================================= */

async function selectPlace(placeName) {

    if (!placeName) {
        return;
    }


    console.log(
        "Selecting place:",
        placeName
    );


    try {

        const response =
            await fetch(
                "/shristi/place/" +
                encodeURIComponent(placeName) +
                "/",
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                }
            );


        if (!response.ok) {

            throw new Error(
                `Place API returned ${response.status}`
            );

        }


        const result =
            await response.json();


        console.log(
            "PLACE API RESPONSE:",
            result
        );


        if (!result.success) {

            throw new Error(
                result.error ||
                "Place could not be loaded."
            );

        }


        currentPlace =
            result.place.name;


        currentPlaceData =
            result.place;


        displaySelectedPlace(
            currentPlaceData
        );


    } catch (error) {

        console.error(
            "SELECT PLACE ERROR:",
            error
        );


        /*
        -----------------------------------------------------
        FALLBACK TO ALREADY LOADED CARD DATA
        -----------------------------------------------------
        */

        const fallbackPlace =
            findPlaceFromCard(
                placeName
            );


        if (fallbackPlace) {

            currentPlace =
                fallbackPlace.name;


            currentPlaceData =
                fallbackPlace;


            displaySelectedPlace(
                fallbackPlace
            );


            return;

        }


        showBotMessage(
            "Unable to load this destination. " +
            error.message
        );

    }

}


/* =========================================================
   FIND PLACE FROM EXISTING CARD
========================================================= */

function findPlaceFromCard(
    placeName
) {

    const cards =
        document.querySelectorAll(
            ".place-card"
        );


    for (
        const card of cards
    ) {

        const cardName =
            card
                .querySelector("h4")
                ?.textContent
                ?.trim();


        if (
            cardName &&
            cardName.toLowerCase() ===
                String(placeName)
                    .toLowerCase()
                    .trim()
        ) {

            return {
                name: cardName,

                category:
                    card
                        .querySelector(
                            ".place-category"
                        )
                        ?.textContent
                        ?.trim() || "",

                description:
                    card
                        .querySelector(
                            ".place-card-content p"
                        )
                        ?.textContent
                        ?.trim() || "",

                location: ""
            };

        }

    }


    return null;

}


/* =========================================================
   SELECT PLACE FROM DROPDOWN
========================================================= */

function selectPlaceFromDropdown(
    placeName
) {

    if (!placeName) {
        return;
    }


    selectPlace(
        placeName
    );

}


/* =========================================================
   DISPLAY SELECTED PLACE
========================================================= */

function displaySelectedPlace(data) {

    if (!data) {
        return;
    }


    currentPlace =
        data.name;


    currentPlaceData =
        data;


    /* -----------------------------------------------------
       UPDATE DROPDOWN
    ----------------------------------------------------- */

    const selector =
        document.getElementById(
            "place-selector"
        );


    if (selector) {

        selector.value =
            data.name || "";

    }


    /* -----------------------------------------------------
       SELECTED PLACE AREA
    ----------------------------------------------------- */

    const selectedArea =
        document.getElementById(
            "selected-place-area"
        );


    const selectedName =
        document.getElementById(
            "selected-place-name"
        );


    if (selectedArea) {

        selectedArea.style.display =
            "block";

    }


    if (selectedName) {

        selectedName.textContent =
            data.name || "";

    }


    /* -----------------------------------------------------
       RIGHT DETAILS PANEL
    ----------------------------------------------------- */

    const emptyState =
        document.getElementById(
            "details-empty-state"
        );


    const details =
        document.getElementById(
            "details-content"
        );


    if (emptyState) {

        emptyState.style.display =
            "none";

    }


    if (details) {

        details.style.display =
            "block";

    }


    setText(
        "panel-title",
        data.name
    );


    setText(
        "panel-category",
        data.category ||
        data.broad_category ||
        "Destination"
    );


    setText(
        "panel-location",
        data.location ||
        data.address ||
        "Delhi"
    );


    setText(
        "panel-rating",
        data.rating ||
        "Not available"
    );


    setText(
        "panel-desc",
        data.description ||
        "Information unavailable."
    );


    setText(
        "panel-time",
        data.best_time_season ||
        data.best_time ||
        "Not available"
    );


    /* -----------------------------------------------------
       ENTRY FEE
    ----------------------------------------------------- */

    let fee = "";


    if (data.entry_fee_indian) {

        fee =
            "Indian: " +
            data.entry_fee_indian;

    }


    if (data.entry_fee_foreigner) {

        if (fee) {
            fee += " | ";
        }


        fee +=
            "Foreign: " +
            data.entry_fee_foreigner;

    }


    if (!fee) {

        fee =
            data.entry_fee ||
            "Not available";

    }


    setText(
        "panel-fee",
        fee
    );


    /* -----------------------------------------------------
       IMAGES
    ----------------------------------------------------- */

    updateMainImage(data);
    updateImageGallery(data);


    /* -----------------------------------------------------
       ACTION PANEL
    ----------------------------------------------------- */

    const actionPanel =
        document.getElementById(
            "action-panel"
        );


    if (actionPanel) {

        actionPanel.style.display =
            "block";

    }


    /* -----------------------------------------------------
       HIDE EXPLORE GRID
    ----------------------------------------------------- */

    const exploreGrid =
        document.getElementById(
            "explore-grid"
        );


    if (exploreGrid) {

        exploreGrid.style.display =
            "none";

    }


    /* -----------------------------------------------------
       CHAT MESSAGE
    ----------------------------------------------------- */

    appendMessage(
        "user",
        `Tell me about ${escapeHTML(
            data.name
        )}`
    );


    setTimeout(function () {

        appendMessage(
            "bot",

            `
            <div class="response-heading">
                ✨ ${escapeHTML(data.name)}
            </div>

            <p>
                I've loaded the information for
                <strong>
                    ${escapeHTML(data.name)}
                </strong>.
            </p>

            <p>
                What would you like to know?
            </p>

            <div class="response-hint">
                📖 About &nbsp; • &nbsp;
                🏛 History &nbsp; • &nbsp;
                🎟 Entry Fee &nbsp; • &nbsp;
                🕐 Best Time &nbsp; • &nbsp;
                📍 How to Reach &nbsp; • &nbsp;
                💡 Travel Tips
            </div>
            `
        );

    }, 300);


    /* -----------------------------------------------------
       MOBILE DETAILS
    ----------------------------------------------------- */

    if (window.innerWidth <= 900) {

        openSidebar("right");

    }

}


/* =========================================================
   MAIN IMAGE
========================================================= */

function updateMainImage(data) {

    const image =
        document.getElementById(
            "panel-image"
        );


    if (!image) {
        return;
    }


    let firstImage = "";


    if (
        Array.isArray(data.images) &&
        data.images.length > 0
    ) {

        firstImage =
            data.images.find(
                img =>
                    typeof img === "string" &&
                    img.trim() !== ""
            ) || "";

    }


    if (!firstImage) {

        firstImage =
            data.image_url ||
            data.image ||
            DEFAULT_PLACE_IMAGE;

    }


    image.src =
        firstImage;


    image.alt =
        data.name ||
        "Place";


    image.onerror =
        function () {

            this.onerror = null;

            this.src =
                DEFAULT_PLACE_IMAGE;

        };

}


/* =========================================================
   FIVE IMAGE GALLERY
========================================================= */

function updateImageGallery(data) {

    const gallery =
        document.getElementById(
            "place-gallery"
        );


    if (!gallery) {

        console.warn(
            "place-gallery element not found."
        );

        return;

    }


    gallery.innerHTML = "";


    let images =
        Array.isArray(data.images)
            ? data.images.filter(
                image =>
                    typeof image === "string" &&
                    image.trim() !== ""
              )
            : [];


    if (
        images.length === 0 &&
        data.image_url
    ) {

        images = [
            data.image_url
        ];

    }


    images
        .slice(0, 5)
        .forEach(function (
            imageURL,
            index
        ) {

            const image =
                document.createElement("img");


            image.src =
                imageURL;


            image.alt =
                `${data.name || "Place"} view ${index + 1}`;


            image.className =
                "place-gallery-image";


            image.loading =
                "lazy";


            image.onclick =
                function () {

                    const mainImage =
                        document.getElementById(
                            "panel-image"
                        );


                    if (mainImage) {

                        mainImage.src =
                            imageURL;

                    }

                };


            image.onerror =
                function () {

                    this.style.display =
                        "none";

                };


            gallery.appendChild(
                image
            );

        });


    console.log(
        `Showing ${Math.min(
            images.length,
            5
        )} images for ${data.name}`
    );

}


/* =========================================================
   CHANGE PLACE
========================================================= */

function changePlace() {

    currentPlace = null;
    currentPlaceData = null;


    /* -----------------------------------------------------
       RESET DROPDOWN
    ----------------------------------------------------- */

    const selector =
        document.getElementById(
            "place-selector"
        );


    if (selector) {

        selector.value = "";

    }


    /* -----------------------------------------------------
       HIDE SELECTED AREA
    ----------------------------------------------------- */

    const selectedArea =
        document.getElementById(
            "selected-place-area"
        );


    if (selectedArea) {

        selectedArea.style.display =
            "none";

    }


    /* -----------------------------------------------------
       HIDE ACTION PANEL
    ----------------------------------------------------- */

    const actionPanel =
        document.getElementById(
            "action-panel"
        );


    if (actionPanel) {

        actionPanel.style.display =
            "none";

    }


    /* -----------------------------------------------------
       SHOW EXPLORE GRID
    ----------------------------------------------------- */

    const exploreGrid =
        document.getElementById(
            "explore-grid"
        );


    if (exploreGrid) {

        exploreGrid.style.display =
            "grid";

    }


    /* -----------------------------------------------------
       RESET DETAILS
    ----------------------------------------------------- */

    const details =
        document.getElementById(
            "details-content"
        );


    const emptyState =
        document.getElementById(
            "details-empty-state"
        );


    if (details) {

        details.style.display =
            "none";

    }


    if (emptyState) {

        emptyState.style.display =
            "flex";

    }


    closeAllSidebars();

}


/* =========================================================
   SEND QUERY
========================================================= */

async function sendQuery(
    intent,
    buttonText
) {

    if (!currentPlace) {

        showBotMessage(
            "Please select a destination first."
        );

        return;

    }


    appendMessage(
        "user",
        escapeHTML(buttonText)
    );


    /* -----------------------------------------------------
       ROUTE
    ----------------------------------------------------- */

    if (intent === "ROUTE") {

        handleRoute();

        return;

    }


    const typingID =
        showTyping();


    try {

        const response =
            await fetch(
                API.chat,
                {

                    method: "POST",

                    credentials: "same-origin",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json",

                        "X-CSRFToken":
                            getCSRFToken()

                    },

                    body:
                        JSON.stringify({

                            question:
                                buildQuestion(
                                    intent
                                )

                        })

                }
            );


        removeTyping(
            typingID
        );


        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "CHATBOT RESPONSE:",
            data
        );


        if (
            !data.success &&
            !data.answer
        ) {

            throw new Error(
                data.error ||
                "Chatbot API failed."
            );

        }


        if (data.answer) {

            appendMessage(
                "bot",
                formatBotResponse(
                    data.answer
                )
            );

        }

        else {

            throw new Error(
                "No answer returned by engine."
            );

        }


    } catch (error) {

        removeTyping(
            typingID
        );


        console.error(
            "CHATBOT ERROR:",
            error
        );


        const fallback =
            generateLocalAnswer(
                intent
            );


        appendMessage(
            "bot",
            fallback
        );

    }

}


/* =========================================================
   BUILD QUESTION
========================================================= */

function buildQuestion(intent) {

    const name =
        currentPlaceData?.name ||
        currentPlace;


    const questions = {

        ABOUT_PLACE:
            `Tell me about ${name}`,

        HISTORY:
            `Tell me the history of ${name}`,

        ENTRY_FEE:
            `What is the entry fee for ${name}?`,

        BEST_TIME:
            `When should I visit ${name}?`,

        ROUTE:
            `How can I reach ${name}?`,

        AWARENESS:
            `Give me travel tips for ${name}`,

        DURATION:
            `How long should I spend at ${name}?`

    };


    return questions[intent] ||
        `Tell me about ${name}`;

}


/* =========================================================
   LOCAL FALLBACK
========================================================= */

function generateLocalAnswer(intent) {

    const data =
        currentPlaceData;


    if (!data) {

        return `
            <div class="response-heading">
                ⚠️ Place not found
            </div>
        `;

    }


    switch (intent) {

        case "ABOUT_PLACE":

            return `

                <div class="response-heading">
                    📖 About ${escapeHTML(
                        data.name
                    )}
                </div>

                <p>
                    ${escapeHTML(
                        data.description ||
                        "Information unavailable."
                    )}
                </p>

            `;


        case "HISTORY":

            return `

                <div class="response-heading">
                    🏛 History of ${escapeHTML(
                        data.name
                    )}
                </div>

                <p>
                    ${escapeHTML(
                        data.history ||
                        "Historical information is currently unavailable."
                    )}
                </p>

            `;


        case "ENTRY_FEE":

            return `

                <div class="response-heading">
                    🎟 Entry Fee — ${escapeHTML(
                        data.name
                    )}
                </div>

                <p>
                    🇮🇳 <strong>Indian:</strong>
                    ${escapeHTML(
                        data.entry_fee_indian ||
                        "Not available"
                    )}
                </p>

                <p>
                    🌍 <strong>Foreign visitors:</strong>
                    ${escapeHTML(
                        data.entry_fee_foreigner ||
                        "Not available"
                    )}
                </p>

            `;


        case "BEST_TIME":

            return `

                <div class="response-heading">
                    🕐 Best Time to Visit
                </div>

                <p>
                    ${escapeHTML(
                        data.best_time_season ||
                        data.best_time ||
                        "Not available"
                    )}
                </p>

                ${
                    data.best_time_suggestion
                        ? `
                            <p>
                                💡 ${escapeHTML(
                                    data.best_time_suggestion
                                )}
                            </p>
                          `
                        : ""
                }

            `;


        case "AWARENESS":

            return `

                <div class="response-heading">
                    💡 Travel Tips
                </div>

                <p>
                    ${escapeHTML(
                        data.tips ||
                        data.awareness_tips ||
                        "Travel tips are currently unavailable."
                    )}
                </p>

            `;


        case "DURATION":

            return `

                <div class="response-heading">
                    🕐 Recommended Duration
                </div>

                <p>
                    ${escapeHTML(
                        data.duration ||
                        "Not available"
                    )}
                </p>

            `;


        default:

            return `

                <div class="response-heading">
                    ✨ ${escapeHTML(
                        data.name
                    )}
                </div>

                <p>
                    Information is currently unavailable.
                </p>

            `;

    }

}


/* =========================================================
   GOOGLE MAPS ROUTE
========================================================= */

function handleRoute() {

    if (!currentPlaceData) {

        showBotMessage(
            "Please select a destination first."
        );

        return;

    }


    const name =
        currentPlaceData.name;


    const latitude =
        currentPlaceData.latitude;


    const longitude =
        currentPlaceData.longitude;


    let googleMapsURL = "";


    if (
        latitude !== undefined &&
        latitude !== null &&
        latitude !== "" &&
        longitude !== undefined &&
        longitude !== null &&
        longitude !== ""
    ) {

        googleMapsURL =
            "https://www.google.com/maps/dir/?api=1" +
            "&destination=" +
            encodeURIComponent(
                `${latitude},${longitude}`
            );

    }

    else if (
        currentPlaceData.google_maps_url
    ) {

        googleMapsURL =
            currentPlaceData.google_maps_url;

    }

    else {

        googleMapsURL =
            "https://www.google.com/maps/dir/?api=1" +
            "&destination=" +
            encodeURIComponent(
                name
            );

    }


    appendMessage(
        "bot",

        `

        <div class="response-heading">
            🗺 Intelligent Route Agent
        </div>

        <p>
            Your destination is
            <strong>
                ${escapeHTML(name)}
            </strong>.
        </p>

        <p>
            Google Maps will calculate the route
            from your current location to this destination.
        </p>

        <button
            class="chat-route-button"
            onclick="openGoogleMaps('${escapeAttribute(
                googleMapsURL
            )}')">

            <i class="fa-solid fa-map-location-dot"></i>

            Open in Google Maps

        </button>

        `

    );

}


/* =========================================================
   OPEN GOOGLE MAPS
========================================================= */

function openGoogleMaps(url) {

    if (!url) {
        return;
    }


    window.open(
        url,
        "_blank",
        "noopener,noreferrer"
    );

}


/* =========================================================
   KEEP OLD FUNCTION NAME
========================================================= */

function openIntelligentRoute() {

    if (!currentPlace) {

        showBotMessage(
            "Please select a destination first."
        );

        return;

    }


    appendMessage(
        "user",
        "📍 Find my best route"
    );


    handleRoute();

}


/* =========================================================
   APPEND MESSAGE
========================================================= */

function appendMessage(
    sender,
    content
) {

    const container =
        document.getElementById(
            "messages-container"
        );


    if (!container) {

        console.error(
            "messages-container not found."
        );

        return;

    }


    const message =
        document.createElement("div");


    message.className =
        `message ${sender}-message`;


    if (sender === "bot") {

        message.innerHTML = `

            <div class="message-avatar">

                <i class="fa-solid fa-compass"></i>

            </div>


            <div class="message-content">

                <div class="message-name">
                    DekhoChat
                </div>


                <div class="message-bubble">

                    ${content}

                </div>

            </div>

        `;

    }

    else {

        message.innerHTML = `

            <div class="message-content user-content">

                <div class="message-bubble">

                    ${content}

                </div>

            </div>

        `;

    }


    container.appendChild(
        message
    );


    scrollChatToBottom();

}


/* =========================================================
   BOT MESSAGE
========================================================= */

function showBotMessage(message) {

    appendMessage(
        "bot",
        `<p>${escapeHTML(message)}</p>`
    );

}


/* =========================================================
   FORMAT ENGINE RESPONSE
========================================================= */

function formatBotResponse(text) {

    if (!text) {

        return "I couldn't find an answer.";

    }


    let html =
        escapeHTML(text);


    /* -----------------------------------------------------
       BOLD
    ----------------------------------------------------- */

    html =
        html.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    /* -----------------------------------------------------
       HEADINGS
    ----------------------------------------------------- */

    html =
        html.replace(
            /^### (.*?)$/gm,
            '<div class="response-heading">$1</div>'
        );


    /* -----------------------------------------------------
       BULLETS
    ----------------------------------------------------- */

    html =
        html.replace(
            /^[-•]\s+(.*?)$/gm,
            "<li>$1</li>"
        );


    /* -----------------------------------------------------
       NUMBERED LIST
    ----------------------------------------------------- */

    html =
        html.replace(
            /^(\d+)\.\s+(.*?)$/gm,
            "<li>$2</li>"
        );


    /* -----------------------------------------------------
       LINE BREAKS
    ----------------------------------------------------- */

    html =
        html.replace(
            /\n/g,
            "<br>"
        );


    return html;

}


/* =========================================================
   TYPING INDICATOR
========================================================= */

function showTyping() {

    const container =
        document.getElementById(
            "messages-container"
        );


    if (!container) {
        return null;
    }


    const id =
        "typing-" +
        Date.now();


    const element =
        document.createElement("div");


    element.id =
        id;


    element.className =
        "message bot-message typing-message";


    element.innerHTML = `

        <div class="message-avatar">

            <i class="fa-solid fa-compass"></i>

        </div>


        <div class="message-content">

            <div class="message-name">
                DekhoChat
            </div>


            <div class="typing-bubble">

                <span></span>
                <span></span>
                <span></span>

            </div>

        </div>

    `;


    container.appendChild(
        element
    );


    scrollChatToBottom();


    return id;

}


/* =========================================================
   REMOVE TYPING
========================================================= */

function removeTyping(id) {

    if (!id) {
        return;
    }


    const element =
        document.getElementById(id);


    if (element) {

        element.remove();

    }

}


/* =========================================================
   SIDEBAR
========================================================= */

function toggleSidebar(side) {

    const sidebar =
        document.getElementById(
            side === "left"
                ? "left-sidebar"
                : "right-sidebar"
        );


    if (!sidebar) {
        return;
    }


    const isOpen =
        sidebar.classList.contains(
            "open"
        );


    closeAllSidebars();


    if (!isOpen) {

        sidebar.classList.add(
            "open"
        );


        showOverlay();

    }

}


/* =========================================================
   OPEN SIDEBAR
========================================================= */

function openSidebar(side) {

    const sidebar =
        document.getElementById(
            side === "left"
                ? "left-sidebar"
                : "right-sidebar"
        );


    if (!sidebar) {
        return;
    }


    closeAllSidebars();


    sidebar.classList.add(
        "open"
    );


    showOverlay();

}


/* =========================================================
   CLOSE SIDEBAR
========================================================= */

function closeSidebar(side) {

    const sidebar =
        document.getElementById(
            side === "left"
                ? "left-sidebar"
                : "right-sidebar"
        );


    if (sidebar) {

        sidebar.classList.remove(
            "open"
        );

    }


    hideOverlay();

}


/* =========================================================
   CLOSE ALL SIDEBARS
========================================================= */

function closeAllSidebars() {

    const left =
        document.getElementById(
            "left-sidebar"
        );


    const right =
        document.getElementById(
            "right-sidebar"
        );


    if (left) {

        left.classList.remove(
            "open"
        );

    }


    if (right) {

        right.classList.remove(
            "open"
        );

    }


    hideOverlay();

}


/* =========================================================
   MOBILE OVERLAY
========================================================= */

function showOverlay() {

    const overlay =
        document.getElementById(
            "mobile-overlay"
        );


    if (overlay) {

        overlay.classList.add(
            "active"
        );

    }

}


function hideOverlay() {

    const overlay =
        document.getElementById(
            "mobile-overlay"
        );


    if (overlay) {

        overlay.classList.remove(
            "active"
        );

    }

}


/* =========================================================
   NAVIGATION
========================================================= */

function showSection(section) {

    console.log(
        "Selected section:",
        section
    );


    closeSidebar(
        "left"
    );

}


/* =========================================================
   SCROLL CHAT
========================================================= */

function scrollChatToBottom() {

    const chat =
        document.getElementById(
            "chat-history"
        );


    if (!chat) {
        return;
    }


    setTimeout(function () {

        chat.scrollTo({

            top:
                chat.scrollHeight,

            behavior:
                "smooth"

        });

    }, 50);

}


/* =========================================================
   SEARCH FILTER
========================================================= */

function initializeSearch() {

    const searchInput =
        document.getElementById(
            "place-search"
        );


    if (!searchInput) {

        console.log(
            "Search box NOT found on this page."
        );

        return;

    }


    console.log(
        "Search box found! Ready to filter."
    );


    searchInput.addEventListener(
        "input",
        function (event) {

            const searchTerm =
                event.target.value
                    .toLowerCase()
                    .trim();


            const placeCards =
                document.querySelectorAll(
                    ".place-card"
                );


            placeCards.forEach(
                function (card) {

                    const nameElement =
                        card.querySelector(
                            "h4"
                        );


                    const categoryElement =
                        card.querySelector(
                            ".place-category"
                        );


                    const placeName =
                        nameElement
                            ? nameElement.textContent
                                .toLowerCase()
                                .trim()
                            : "";


                    const placeCategory =
                        categoryElement
                            ? categoryElement.textContent
                                .toLowerCase()
                                .trim()
                            : "";


                    const matches =
                        placeName.includes(
                            searchTerm
                        ) ||
                        placeCategory.includes(
                            searchTerm
                        );


                    card.style.display =
                        matches
                            ? ""
                            : "none";

                }
            );

        }
    );

}


/* =========================================================
   SET TEXT
========================================================= */

function setText(
    id,
    value
) {

    const element =
        document.getElementById(
            id
        );


    if (element) {

        element.textContent =
            value || "";

    }

}


/* =========================================================
   CSRF TOKEN
========================================================= */

function getCSRFToken() {

    return getCookie(
        "csrftoken"
    );

}


function getCookie(name) {

    let cookieValue =
        null;


    if (
        document.cookie &&
        document.cookie !== ""
    ) {

        const cookies =
            document.cookie.split(";");


        for (
            let cookie of cookies
        ) {

            cookie =
                cookie.trim();


            if (
                cookie.startsWith(
                    name + "="
                )
            ) {

                cookieValue =
                    decodeURIComponent(
                        cookie.substring(
                            name.length + 1
                        )
                    );

                break;

            }

        }

    }


    return cookieValue;

}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


/* =========================================================
   ATTRIBUTE ESCAPE
========================================================= */

function escapeAttribute(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        );

}