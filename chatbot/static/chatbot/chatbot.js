/* =========================================================
   DEKHOCHAT
   GoPlan AI Travel Assistant
   CLEAN VERSION + INTELLIGENT MAP ROUTING
========================================================= */


/* =========================================================
   GLOBAL STATE
========================================================= */

let currentPlace = null;
let currentPlaceData = null;


/* =========================================================
   API URLS
========================================================= */

const API = {
    places: "/shristi/places/",
    chat: "/shristi/api/"
};


/* =========================================================
   PAGE INITIALIZATION
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("DekhoChat initialized.");

    loadAllPlaces();

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
   LOAD ALL 81 PLACES
========================================================= */

async function loadAllPlaces() {

    const selector =
        document.getElementById("place-selector");

    const grid =
        document.getElementById("explore-grid");


    try {

        const response =
            await fetch(API.places);


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


        /* -----------------------------------------------------
           SELECT DROPDOWN
        ----------------------------------------------------- */

        if (selector) {

            selector.innerHTML = "";

            const defaultOption =
                document.createElement("option");


            defaultOption.value = "";

            defaultOption.textContent =
                "Select a place from 81 destinations...";


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


        /* -----------------------------------------------------
           PLACE CARDS
        ----------------------------------------------------- */

        if (grid) {

            grid.innerHTML = "";


            places.forEach(function (place) {

                const card =
                    createPlaceCard(place);


                grid.appendChild(card);

            });

        }


    } catch (error) {

        console.error(
            "LOAD PLACES ERROR:",
            error
        );


        if (grid) {

            grid.innerHTML = `
                <div class="place-load-error">

                    ⚠️ Unable to load destinations.

                    <br>

                    <small>
                        ${escapeHTML(error.message)}
                    </small>

                </div>
            `;

        }

    }

}


/* =========================================================
   CREATE PLACE CARD
========================================================= */

function createPlaceCard(place) {

    const article =
        document.createElement("article");


    article.className =
        "place-card";


    article.onclick = function () {

        selectPlace(place.name);

    };


    /* ---------------------------------------------------------
       IMAGE
    --------------------------------------------------------- */

    let image = "";


    if (
        place.images &&
        Array.isArray(place.images) &&
        place.images.length > 0
    ) {

        image =
            place.images[0];

    }


    if (!image) {

        image =
            "/static/chatbot/places/0/image_1.jpeg";

    }


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


    const remoteImage =
        place.remote_images &&
        Array.isArray(place.remote_images) &&
        place.remote_images.length
            ? place.remote_images[0]
            : "";

    article.innerHTML = `

        <div class="place-image-wrapper">

            <img
                src="${escapeAttribute(image)}"
                alt="${escapeAttribute(place.name)}"
            >

            <span class="place-category">
                ${escapeHTML(category)}
            </span>

        </div>


        <div class="place-card-content">

            <h4>
                ${escapeHTML(place.name)}
            </h4>

            <p>
                ${escapeHTML(
                    description.substring(0, 140)
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

    const cardImage = article.querySelector("img");
    if (cardImage) {
        cardImage.addEventListener("error", function () {
            const fallback = remoteImage ||
                "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=900&q=85";
            if (this.dataset.fallbackUsed !== "1" && fallback) {
                this.dataset.fallbackUsed = "1";
                this.src = fallback;
            } else {
                this.style.display = "none";
            }
        });
    }

    return article;

}


/* =========================================================
   SELECT PLACE
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
                "/"
            );


        if (!response.ok) {

            throw new Error(
                `Place API returned ${response.status}`
            );

        }


        const result =
            await response.json();


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


        showBotMessage(
            "Unable to load this destination. " +
            error.message
        );

    }

}


/* =========================================================
   SELECT PLACE FROM DROPDOWN
========================================================= */

function selectPlaceFromDropdown(placeName) {

    if (!placeName) {
        return;
    }


    selectPlace(placeName);

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


    /* ---------------------------------------------------------
       UPDATE DROPDOWN
    --------------------------------------------------------- */

    const selector =
        document.getElementById(
            "place-selector"
        );


    if (selector) {

        selector.value =
            data.name || "";

    }


    /* ---------------------------------------------------------
       SELECTED PLACE AREA
    --------------------------------------------------------- */

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


    /* ---------------------------------------------------------
       RIGHT DETAILS PANEL
    --------------------------------------------------------- */

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
        data.address
    );


    setText(
        "panel-rating",
        data.rating
            ? data.rating
            : "Not available"
    );


    setText(
        "panel-desc",
        data.description
    );


    setText(
        "panel-time",
        data.best_time_season ||
        data.best_time ||
        "Not available"
    );


    /* ---------------------------------------------------------
       ENTRY FEE
    --------------------------------------------------------- */

    let fee = "";


    if (data.entry_fee_indian) {

        fee +=
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
            "Not available";

    }


    setText(
        "panel-fee",
        fee
    );


    /* ---------------------------------------------------------
       MAIN IMAGE
    --------------------------------------------------------- */

    updateMainImage(data);


    /* ---------------------------------------------------------
       IMAGE GALLERY
    --------------------------------------------------------- */

    updateImageGallery(data);


    /* ---------------------------------------------------------
       SHOW ACTION PANEL
    --------------------------------------------------------- */

    const actionPanel =
        document.getElementById(
            "action-panel"
        );


    if (actionPanel) {

        actionPanel.style.display =
            "block";

    }


    /* ---------------------------------------------------------
       HIDE PLACE GRID
    --------------------------------------------------------- */

    const exploreGrid =
        document.getElementById(
            "explore-grid"
        );


    if (exploreGrid) {

        exploreGrid.style.display =
            "none";

    }


    /* ---------------------------------------------------------
       CHAT MESSAGE
    --------------------------------------------------------- */

    appendMessage(
        "user",
        `Tell me about ${escapeHTML(data.name)}`
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


    /* ---------------------------------------------------------
       OPEN DETAILS ON MOBILE
    --------------------------------------------------------- */

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
            data.images[0];

    }


    if (!firstImage) {

        firstImage =
            "/static/chatbot/places/0/image_1.jpeg";

    }


    image.src =
        firstImage;


    image.alt =
        data.name || "Place";

    image.dataset.fallbackUsed = "0";

    image.onerror =
        function () {

            const fallbacks =
                Array.isArray(data.remote_images)
                    ? data.remote_images
                    : [];

            const fallback = fallbacks[0] ||
                "/static/chatbot/places/0/image_1.jpeg";

            if (this.dataset.fallbackUsed !== "1" && fallback !== this.src) {
                this.dataset.fallbackUsed = "1";
                this.src = fallback;
            } else {
                this.style.display = "none";
            }

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


    const images =
        Array.isArray(data.images)
            ? data.images
            : [];


    images
        .slice(0, 5)
        .forEach(function (imageURL, index) {

            if (!imageURL) {
                return;
            }


            const image =
                document.createElement("img");


            image.src =
                imageURL;


            image.alt =
                `${data.name} view ${index + 1}`;


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


            image.dataset.fallbackUsed = "0";

            image.onerror =
                function () {

                    const fallbackList =
                        Array.isArray(data.remote_images)
                            ? data.remote_images
                            : [];

                    const fallback = fallbackList[index] || fallbackList[0] || "";

                    if (this.dataset.fallbackUsed !== "1" && fallback && fallback !== this.src) {
                        this.dataset.fallbackUsed = "1";
                        this.src = fallback;
                    } else {
                        this.style.display = "none";
                    }

                };


            gallery.appendChild(
                image
            );

        });


    console.log(
        `Showing ${Math.min(images.length, 5)} images for ${data.name}`
    );

}


/* =========================================================
   CHANGE PLACE
========================================================= */

function changePlace() {

    currentPlace = null;

    currentPlaceData = null;


    const selector =
        document.getElementById(
            "place-selector"
        );


    if (selector) {

        selector.value = "";

    }


    const selectedArea =
        document.getElementById(
            "selected-place-area"
        );


    if (selectedArea) {

        selectedArea.style.display =
            "none";

    }


    const actionPanel =
        document.getElementById(
            "action-panel"
        );


    if (actionPanel) {

        actionPanel.style.display =
            "none";

    }


    const exploreGrid =
        document.getElementById(
            "explore-grid"
        );


    if (exploreGrid) {

        exploreGrid.style.display =
            "grid";

    }


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


    /* ---------------------------------------------------------
       ROUTE
    --------------------------------------------------------- */

    if (intent === "ROUTE") {

        handleRoute();

        return;

    }


    /* ---------------------------------------------------------
       TYPING
    --------------------------------------------------------- */

    const typingID =
        showTyping();


    try {

        const response =
            await fetch(
                API.chat,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "X-CSRFToken":
                            getCSRFToken()

                    },

                    body:
                        JSON.stringify({

                            question:
                                buildQuestion(intent)

                        })

                }
            );


        removeTyping(typingID);


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

        removeTyping(typingID);


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
   BUILD QUESTION FOR ENGINE
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
                    📖 About ${escapeHTML(data.name)}
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
                    🏛 History of ${escapeHTML(data.name)}
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
                    🎟 Entry Fee — ${escapeHTML(data.name)}
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
                    ✨ ${escapeHTML(data.name)}
                </div>

                <p>
                    Information is currently unavailable.
                </p>

            `;

    }

}


/* =========================================================
   INTELLIGENT MAP ROUTE
========================================================= */

function getSelectedDestination() {

    if (!currentPlaceData) {
        return null;
    }


    const name =
        currentPlaceData.name ||
        currentPlace ||
        "Destination";


    const latitude =
        Number(
            currentPlaceData.latitude ??
            currentPlaceData.lat
        );


    const longitude =
        Number(
            currentPlaceData.longitude ??
            currentPlaceData.lon ??
            currentPlaceData.lng
        );


    return {

        name: name,

        latitude:
            Number.isFinite(latitude)
                ? latitude
                : null,

        longitude:
            Number.isFinite(longitude)
                ? longitude
                : null

    };

}


/* =========================================================
   BUILD INTELLIGENT MAP URL
========================================================= */

function buildIntelligentMapURL(destination) {

    if (!destination) {
        return null;
    }


    const params =
        new URLSearchParams();


    /*
       Tell Intelligent Map that the starting point
       should be the user's current location.
    */

    params.set(
        "from",
        "current"
    );


    /*
       Destination name
    */

    params.set(
        "to",
        destination.name
    );


    /*
       Automatically calculate route
    */

    params.set(
        "auto_route",
        "1"
    );


    /*
       Pass coordinates when available.
       This avoids unnecessary geocoding.
    */

    if (
        Number.isFinite(
            destination.latitude
        )
    ) {

        params.set(
            "lat",
            String(destination.latitude)
        );

    }


    if (
        Number.isFinite(
            destination.longitude
        )
    ) {

        params.set(
            "lon",
            String(destination.longitude)
        );

    }


    return (
        "/map/?" +
        params.toString()
    );

}


/* =========================================================
   HANDLE ROUTE
========================================================= */

function handleRoute() {

    if (!currentPlaceData) {

        showBotMessage(
            "Please select a destination first."
        );

        return;

    }


    const destination =
        getSelectedDestination();


    if (!destination) {

        showBotMessage(
            "Destination information is unavailable."
        );

        return;

    }


    const intelligentMapURL =
        buildIntelligentMapURL(
            destination
        );


    if (!intelligentMapURL) {

        showBotMessage(
            "Unable to create Intelligent Map route."
        );

        return;

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
                ${escapeHTML(destination.name)}
            </strong>.

        </p>

        <p>

            DekhoBharat Intelligent Map will
            calculate the best route from your
            current location.

        </p>

        <button
            class="chat-route-button"
            onclick="openIntelligentMap('${escapeAttribute(intelligentMapURL)}')"
        >

            <i class="fa-solid fa-map-location-dot"></i>

            Open Intelligent Map

        </button>

        `

    );

}


/* =========================================================
   OPEN INTELLIGENT MAP
========================================================= */

function openIntelligentMap(url) {

    if (!url) {
        return;
    }


    console.log(
        "Opening Intelligent Map:",
        url
    );


    window.location.href =
        url;

}


/* =========================================================
   GOOGLE MAPS FALLBACK
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
   OLD FUNCTION NAME
   KEPT FOR HTML COMPATIBILITY
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


    html =
        html.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    html =
        html.replace(
            /^### (.*?)$/gm,
            '<div class="response-heading">$1</div>'
        );


    html =
        html.replace(
            /^[-•]\s+(.*?)$/gm,
            "<li>$1</li>"
        );


    html =
        html.replace(
            /^(\d+)\.\s+(.*?)$/gm,
            "<li>$2</li>"
        );


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


    /*
    ---------------------------------------------------------
    For now keep existing design.
    ---------------------------------------------------------
    */

    closeSidebar("left");

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
   SET TEXT
========================================================= */

function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);


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


/* =========================================================
   SEARCH FILTER LOGIC
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

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
                            nameElement?.textContent
                                ?.toLowerCase()
                                ?.trim() ||
                            "";


                        const placeCategory =
                            categoryElement?.textContent
                                ?.toLowerCase()
                                ?.trim() ||
                            "";


                        /*
                        -------------------------------------------------
                        MATCH PLACE NAME OR CATEGORY
                        -------------------------------------------------
                        */

                        if (
                            placeName.includes(
                                searchTerm
                            ) ||

                            placeCategory.includes(
                                searchTerm
                            )
                        ) {

                            card.style.display =
                                "flex";

                        }

                        else {

                            card.style.display =
                                "none";

                        }

                    }
                );

            }
        );

    }
);
/* =========================================================
   DEKHOBHARAT INTELLIGENT MAP
   FINAL ROUTE SYSTEM
========================================================= */


/* =========================================================
   GET SELECTED DESTINATION
========================================================= */

function getSelectedDestination() {

    if (!currentPlaceData) {

        return null;

    }


    const name =
        currentPlaceData.name ||
        currentPlace ||
        "Destination";


    /*
    ---------------------------------------------------------
    SUPPORT MULTIPLE POSSIBLE FIELD NAMES
    ---------------------------------------------------------
    */

    const latitude =
        Number(
            currentPlaceData.latitude ??
            currentPlaceData.lat ??
            currentPlaceData.location_latitude
        );


    const longitude =
        Number(
            currentPlaceData.longitude ??
            currentPlaceData.lon ??
            currentPlaceData.lng ??
            currentPlaceData.location_longitude
        );


    return {

        name: name,

        latitude:
            Number.isFinite(latitude)
                ? latitude
                : null,

        longitude:
            Number.isFinite(longitude)
                ? longitude
                : null

    };

}


/* =========================================================
   BUILD INTELLIGENT MAP URL
========================================================= */

function buildIntelligentMapURL(
    destination
) {

    if (!destination) {

        return null;

    }


    const params =
        new URLSearchParams();


    /*
    ---------------------------------------------------------
    START FROM USER'S CURRENT LOCATION
    ---------------------------------------------------------
    */

    params.set(
        "from",
        "current"
    );


    /*
    ---------------------------------------------------------
    DESTINATION NAME
    ---------------------------------------------------------
    */

    params.set(
        "to",
        destination.name
    );


    /*
    ---------------------------------------------------------
    AUTO CALCULATE ROUTE
    ---------------------------------------------------------
    */

    params.set(
        "auto_route",
        "1"
    );


    /*
    ---------------------------------------------------------
    DESTINATION LATITUDE
    ---------------------------------------------------------
    */

    if (
        Number.isFinite(
            destination.latitude
        )
    ) {

        params.set(
            "lat",
            String(
                destination.latitude
            )
        );

    }


    /*
    ---------------------------------------------------------
    DESTINATION LONGITUDE
    ---------------------------------------------------------
    */

    if (
        Number.isFinite(
            destination.longitude
        )
    ) {

        params.set(
            "lon",
            String(
                destination.longitude
            )
        );

    }


    /*
    ---------------------------------------------------------
    FINAL URL
    ---------------------------------------------------------
    */

    return (
        "/map/?" +
        params.toString()
    );

}


/* =========================================================
   HANDLE ROUTE
========================================================= */

function handleRoute() {

    /*
    ---------------------------------------------------------
    CHECK DESTINATION
    ---------------------------------------------------------
    */

    if (!currentPlaceData) {

        showBotMessage(
            "Please select a destination first."
        );

        return;

    }


    /*
    ---------------------------------------------------------
    GET DESTINATION
    ---------------------------------------------------------
    */

    const destination =
        getSelectedDestination();


    if (!destination) {

        showBotMessage(
            "Destination information is unavailable."
        );

        return;

    }


    /*
    ---------------------------------------------------------
    BUILD MAP URL
    ---------------------------------------------------------
    */

    const intelligentMapURL =
        buildIntelligentMapURL(
            destination
        );


    if (!intelligentMapURL) {

        showBotMessage(
            "Unable to create Intelligent Map route."
        );

        return;

    }


    console.log(
        "INTELLIGENT MAP URL:",
        intelligentMapURL
    );


    /*
    ---------------------------------------------------------
    SHOW ROUTE BUTTON
    ---------------------------------------------------------
    */

    appendMessage(

        "bot",

        `

        <div class="response-heading">

            🗺 Intelligent Route Agent

        </div>


        <p>

            Your destination is

            <strong>
                ${escapeHTML(
                    destination.name
                )}
            </strong>.

        </p>


        <p>

            DekhoBharat Intelligent Map
            will calculate the route from
            your current location.

        </p>


        <button

            class="chat-route-button"

            onclick="
                openIntelligentMap(
                    '${escapeAttribute(
                        intelligentMapURL
                    )}'
                )
            "

        >

            <i class="fa-solid fa-map-location-dot"></i>

            Open Intelligent Map

        </button>

        `

    );

}


/* =========================================================
   OPEN INTELLIGENT MAP
========================================================= */

function openIntelligentMap(url) {

    if (!url) {

        console.error(
            "Intelligent Map URL is empty."
        );

        return;

    }


    console.log(
        "Opening Intelligent Map:",
        url
    );


    /*
    ---------------------------------------------------------
    SAME TAB
    ---------------------------------------------------------
    */

    window.location.href =
        url;

}


/* =========================================================
   OPEN INTELLIGENT ROUTE
   HTML COMPATIBILITY FUNCTION
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
   OPTIONAL GOOGLE MAPS FALLBACK
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
   SEARCH FILTER — FINAL SAFE VERSION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const searchInput =
            document.getElementById(
                "place-search"
            );


        if (!searchInput) {

            return;

        }


        searchInput.addEventListener(
            "input",
            function (event) {

                const searchTerm =
                    (
                        event.target.value ||
                        ""
                    )
                    .toLowerCase()
                    .trim();


                const cards =
                    document.querySelectorAll(
                        ".place-card"
                    );


                cards.forEach(
                    function (card) {

                        const name =
                            card.querySelector(
                                "h4"
                            )?.textContent
                            ?.toLowerCase()
                            ?.trim() || "";


                        const category =
                            card.querySelector(
                                ".place-category"
                            )?.textContent
                            ?.toLowerCase()
                            ?.trim() || "";


                        const matches =
                            name.includes(
                                searchTerm
                            ) ||

                            category.includes(
                                searchTerm
                            );


                        card.style.display =
                            matches
                                ? "flex"
                                : "none";

                    }
                );

            }
        );

    }
);


/* =========================================================
   DEBUG INFORMATION
========================================================= */

console.log(
    "========================================"
);

console.log(
    "DekhoBharat DekhoChat JS loaded."
);

console.log(
    "Intelligent Map routing enabled."
);

console.log(
    "Route endpoint: /map/"
);

console.log(
    "========================================"
);