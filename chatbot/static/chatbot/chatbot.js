/* =========================================================
   DEKHOCHAT
   GoPlan AI Travel Assistant
<<<<<<< HEAD
   CLEAN VERSION
=======
   CLEAN + FIXED VERSION
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
========================================================= */


/* =========================================================
   GLOBAL STATE
========================================================= */

let currentPlace = null;
let currentPlaceData = null;


/* =========================================================
   API URLS
<<<<<<< HEAD
========================================================= */

const API = {

    places: "/shristi/places/",
    chat: "/shristi/api/"

=======
   Django chatbot app is mounted at /shristi/
========================================================= */

const API = {
    places: "/shristi/places/",
    chat: "/shristi/api/"
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
};


/* =========================================================
<<<<<<< HEAD
=======
   DEFAULT IMAGE
========================================================= */

const DEFAULT_PLACE_IMAGE =
    "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1000&q=85";


/* =========================================================
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
   PAGE INITIALIZATION
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("DekhoChat initialized.");

    loadAllPlaces();
<<<<<<< HEAD
=======
    initializeSearch();
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

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
<<<<<<< HEAD
   LOAD ALL 81 PLACES
=======
   LOAD ALL PLACES
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
   Django -> /shristi/places/
========================================================= */

async function loadAllPlaces() {

    const selector =
        document.getElementById("place-selector");

    const grid =
        document.getElementById("explore-grid");


    try {

<<<<<<< HEAD
        const response = await fetch(API.places);
=======
        console.log("Loading destinations...");


        const response =
            await fetch(API.places, {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            });

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

        if (!response.ok) {

            throw new Error(
                `Places API returned ${response.status}`
            );

        }


<<<<<<< HEAD
        const data = await response.json();
=======
        const data =
            await response.json();

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

        console.log(
            "PLACES API RESPONSE:",
            data
        );


        if (!data.success) {

            throw new Error(
<<<<<<< HEAD
                data.error || "Could not load places."
=======
                data.error ||
                "Could not load places."
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            );

        }


        const places =
            Array.isArray(data.places)
                ? data.places
                : [];


        console.log(
            `Loaded ${places.length} places.`
        );


<<<<<<< HEAD
        /*
        -----------------------------------------------------
        SELECT DROPDOWN
        -----------------------------------------------------
        */

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


        /*
        -----------------------------------------------------
        PLACE CARDS
        -----------------------------------------------------
        */

        if (grid) {

            grid.innerHTML = "";

            places.forEach(function (place) {

                const card =
                    createPlaceCard(place);

                grid.appendChild(card);

            });

        }
=======
        populatePlaceDropdown(
            selector,
            places
        );


        populatePlaceGrid(
            grid,
            places
        );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


    } catch (error) {

        console.error(
            "LOAD PLACES ERROR:",
            error
        );


<<<<<<< HEAD
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
=======
        showPlaceLoadError(
            grid,
            error
        );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    }

}


/* =========================================================
<<<<<<< HEAD
=======
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
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
   CREATE PLACE CARD
========================================================= */

function createPlaceCard(place) {

    const article =
        document.createElement("article");

<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    article.className =
        "place-card";


<<<<<<< HEAD
    article.onclick = function () {

        selectPlace(place.name);
=======
    article.dataset.placeName =
        place.name || "";


    article.onclick = function () {

        selectPlace(
            place.name
        );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    };


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    IMAGE
    ---------------------------------------------------------
    */

    let image = "";

    if (
        place.images &&
=======
    /* -----------------------------------------------------
       IMAGE
    ----------------------------------------------------- */

    let image = "";


    if (
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        Array.isArray(place.images) &&
        place.images.length > 0
    ) {

<<<<<<< HEAD
        image = place.images[0];
=======
        image =
            place.images.find(
                img =>
                    typeof img === "string" &&
                    img.trim() !== ""
            ) || "";
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    }


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    FALLBACK IMAGE
    ---------------------------------------------------------
    */

    if (!image) {

        image =
            "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=900&q=85";
=======
    if (!image) {

        image =
            place.image_url ||
            place.image ||
            "";
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    }


<<<<<<< HEAD
=======
    if (!image) {

        image =
            DEFAULT_PLACE_IMAGE;

    }


    /* -----------------------------------------------------
       BASIC DATA
    ----------------------------------------------------- */

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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


<<<<<<< HEAD
=======
    const safeDescription =
        String(description);


>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    article.innerHTML = `

        <div class="place-image-wrapper">

            <img
                src="${escapeAttribute(image)}"
<<<<<<< HEAD
                alt="${escapeAttribute(place.name)}"
                onerror="this.src='https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=900&q=85';"
=======
                alt="${escapeAttribute(
                    place.name || "Place"
                )}"
                loading="lazy"
                onerror="this.onerror=null;this.src='${DEFAULT_PLACE_IMAGE}'"
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            >

            <span class="place-category">
                ${escapeHTML(category)}
            </span>

        </div>


        <div class="place-card-content">

            <h4>
<<<<<<< HEAD
                ${escapeHTML(place.name)}
            </h4>

            <p>
                ${escapeHTML(
                    description.substring(0, 140)
=======
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
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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
<<<<<<< HEAD
=======
   Django -> /shristi/place/<place_name>/
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
========================================================= */

async function selectPlace(placeName) {

    if (!placeName) {
        return;
    }


    console.log(
        "Selecting place:",
        placeName
    );


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    GET PLACE DATA FROM DJANGO
    ---------------------------------------------------------
    */

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    try {

        const response =
            await fetch(
                "/shristi/place/" +
                encodeURIComponent(placeName) +
<<<<<<< HEAD
                "/"
=======
                "/",
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                }
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            );


        if (!response.ok) {

            throw new Error(
                `Place API returned ${response.status}`
            );

        }


        const result =
            await response.json();


<<<<<<< HEAD
=======
        console.log(
            "PLACE API RESPONSE:",
            result
        );


>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        if (!result.success) {

            throw new Error(
                result.error ||
                "Place could not be loaded."
            );

        }


        currentPlace =
            result.place.name;

<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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


<<<<<<< HEAD
=======
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


>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        showBotMessage(
            "Unable to load this destination. " +
            error.message
        );

    }

}


/* =========================================================
<<<<<<< HEAD
   SELECT PLACE FROM DROPDOWN
========================================================= */

function selectPlaceFromDropdown(placeName) {
=======
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
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    if (!placeName) {
        return;
    }


<<<<<<< HEAD
    selectPlace(placeName);
=======
    selectPlace(
        placeName
    );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

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

<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    currentPlaceData =
        data;


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    UPDATE DROPDOWN
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       UPDATE DROPDOWN
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    const selector =
        document.getElementById(
            "place-selector"
        );


    if (selector) {

        selector.value =
            data.name || "";

    }


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    SELECTED PLACE AREA
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       SELECTED PLACE AREA
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

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


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    RIGHT DETAILS PANEL
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       RIGHT DETAILS PANEL
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

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
<<<<<<< HEAD
        data.address
=======
        data.address ||
        "Delhi"
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    );


    setText(
        "panel-rating",
<<<<<<< HEAD
        data.rating
            ? data.rating
            : "Not available"
=======
        data.rating ||
        "Not available"
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    );


    setText(
        "panel-desc",
<<<<<<< HEAD
        data.description
=======
        data.description ||
        "Information unavailable."
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    );


    setText(
        "panel-time",
        data.best_time_season ||
        data.best_time ||
        "Not available"
    );


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    ENTRY FEE
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       ENTRY FEE
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    let fee = "";


    if (data.entry_fee_indian) {

<<<<<<< HEAD
        fee +=
=======
        fee =
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            "Indian: " +
            data.entry_fee_indian;

    }


    if (data.entry_fee_foreigner) {

        if (fee) {
            fee += " | ";
        }

<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        fee +=
            "Foreign: " +
            data.entry_fee_foreigner;

    }


    if (!fee) {

        fee =
<<<<<<< HEAD
=======
            data.entry_fee ||
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            "Not available";

    }


    setText(
        "panel-fee",
        fee
    );


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    MAIN IMAGE
    ---------------------------------------------------------
    */

    updateMainImage(data);


    /*
    ---------------------------------------------------------
    5 IMAGE GALLERY
    ---------------------------------------------------------
    */

    updateImageGallery(data);


    /*
    ---------------------------------------------------------
    SHOW ACTION PANEL
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       IMAGES
    ----------------------------------------------------- */

    updateMainImage(data);
    updateImageGallery(data);


    /* -----------------------------------------------------
       ACTION PANEL
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    const actionPanel =
        document.getElementById(
            "action-panel"
        );


    if (actionPanel) {

        actionPanel.style.display =
            "block";

    }


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    HIDE PLACE GRID
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       HIDE EXPLORE GRID
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    const exploreGrid =
        document.getElementById(
            "explore-grid"
        );


    if (exploreGrid) {

        exploreGrid.style.display =
            "none";

    }


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    CHAT MESSAGE
    ---------------------------------------------------------
    */

    appendMessage(
        "user",
        `Tell me about ${escapeHTML(data.name)}`
=======
    /* -----------------------------------------------------
       CHAT MESSAGE
    ----------------------------------------------------- */

    appendMessage(
        "user",
        `Tell me about ${escapeHTML(
            data.name
        )}`
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    OPEN DETAILS ON MOBILE
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       MOBILE DETAILS
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

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
<<<<<<< HEAD
            data.images[0];
=======
            data.images.find(
                img =>
                    typeof img === "string" &&
                    img.trim() !== ""
            ) || "";
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    }


    if (!firstImage) {

        firstImage =
<<<<<<< HEAD
            "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1000&q=85";
=======
            data.image_url ||
            data.image ||
            DEFAULT_PLACE_IMAGE;
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    }


    image.src =
        firstImage;


    image.alt =
<<<<<<< HEAD
        data.name || "Place";
=======
        data.name ||
        "Place";
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


    image.onerror =
        function () {

            this.onerror = null;

            this.src =
<<<<<<< HEAD
                "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1000&q=85";
=======
                DEFAULT_PLACE_IMAGE;
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

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


<<<<<<< HEAD
    const images =
        Array.isArray(data.images)
            ? data.images
            : [];


    /*
    ---------------------------------------------------------
    ONLY SHOW AVAILABLE IMAGES
    ---------------------------------------------------------
    */

    images
        .slice(0, 5)
        .forEach(function (imageURL, index) {

            if (!imageURL) {
                return;
            }

=======
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
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

            const image =
                document.createElement("img");


            image.src =
                imageURL;


            image.alt =
<<<<<<< HEAD
                `${data.name} view ${index + 1}`;
=======
                `${data.name || "Place"} view ${index + 1}`;
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


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
<<<<<<< HEAD
        `Showing ${Math.min(images.length, 5)} images for ${data.name}`
=======
        `Showing ${Math.min(
            images.length,
            5
        )} images for ${data.name}`
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    );

}


/* =========================================================
   CHANGE PLACE
========================================================= */

function changePlace() {

    currentPlace = null;
<<<<<<< HEAD

    currentPlaceData = null;


    /*
    ---------------------------------------------------------
    RESET DROPDOWN
    ---------------------------------------------------------
    */
=======
    currentPlaceData = null;


    /* -----------------------------------------------------
       RESET DROPDOWN
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    const selector =
        document.getElementById(
            "place-selector"
        );


    if (selector) {

        selector.value = "";

    }


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    HIDE SELECTED AREA
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       HIDE SELECTED AREA
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    const selectedArea =
        document.getElementById(
            "selected-place-area"
        );


    if (selectedArea) {

        selectedArea.style.display =
            "none";

    }


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    HIDE ACTION PANEL
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       HIDE ACTION PANEL
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    const actionPanel =
        document.getElementById(
            "action-panel"
        );


    if (actionPanel) {

        actionPanel.style.display =
            "none";

    }


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    SHOW ALL PLACE CARDS
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       SHOW EXPLORE GRID
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    const exploreGrid =
        document.getElementById(
            "explore-grid"
        );


    if (exploreGrid) {

        exploreGrid.style.display =
            "grid";

    }


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    RESET DETAILS
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       RESET DETAILS
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

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


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    USER MESSAGE
    ---------------------------------------------------------
    */

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    appendMessage(
        "user",
        escapeHTML(buttonText)
    );


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    ROUTE
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       ROUTE
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    if (intent === "ROUTE") {

        handleRoute();

        return;

    }


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    TYPING
    ---------------------------------------------------------
    */

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    const typingID =
        showTyping();


    try {

        const response =
            await fetch(
                API.chat,
                {

                    method: "POST",

<<<<<<< HEAD
=======
                    credentials: "same-origin",

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
                    headers: {

                        "Content-Type":
                            "application/json",

<<<<<<< HEAD
=======
                        "Accept":
                            "application/json",

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
                        "X-CSRFToken":
                            getCSRFToken()

                    },

                    body:
                        JSON.stringify({

                            question:
<<<<<<< HEAD
                                buildQuestion(intent)
=======
                                buildQuestion(
                                    intent
                                )
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

                        })

                }
            );


<<<<<<< HEAD
        removeTyping(typingID);
=======
        removeTyping(
            typingID
        );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


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

<<<<<<< HEAD
        removeTyping(typingID);
=======
        removeTyping(
            typingID
        );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


        console.error(
            "CHATBOT ERROR:",
            error
        );


<<<<<<< HEAD
        /*
        -----------------------------------------------------
        IMPORTANT:
        USE LOCAL DATA IF API FAILS
        -----------------------------------------------------
        */

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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
<<<<<<< HEAD
   BUILD QUESTION FOR ENGINE
=======
   BUILD QUESTION
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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
<<<<<<< HEAD
                <div class="response-heading">
                    📖 About ${escapeHTML(data.name)}
=======

                <div class="response-heading">
                    📖 About ${escapeHTML(
                        data.name
                    )}
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
                </div>

                <p>
                    ${escapeHTML(
                        data.description ||
                        "Information unavailable."
                    )}
                </p>
<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            `;


        case "HISTORY":

            return `
<<<<<<< HEAD
                <div class="response-heading">
                    🏛 History of ${escapeHTML(data.name)}
=======

                <div class="response-heading">
                    🏛 History of ${escapeHTML(
                        data.name
                    )}
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
                </div>

                <p>
                    ${escapeHTML(
                        data.history ||
                        "Historical information is currently unavailable."
                    )}
                </p>
<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            `;


        case "ENTRY_FEE":

            return `
<<<<<<< HEAD
                <div class="response-heading">
                    🎟 Entry Fee — ${escapeHTML(data.name)}
=======

                <div class="response-heading">
                    🎟 Entry Fee — ${escapeHTML(
                        data.name
                    )}
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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
<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            `;


        case "BEST_TIME":

            return `
<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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
<<<<<<< HEAD
                        <p>
                            💡 ${escapeHTML(
                                data.best_time_suggestion
                            )}
                        </p>
                        `
                        : ""
                }
=======
                            <p>
                                💡 ${escapeHTML(
                                    data.best_time_suggestion
                                )}
                            </p>
                          `
                        : ""
                }

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            `;


        case "AWARENESS":

            return `
<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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
<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            `;


        case "DURATION":

            return `
<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
                <div class="response-heading">
                    🕐 Recommended Duration
                </div>

                <p>
                    ${escapeHTML(
                        data.duration ||
                        "Not available"
                    )}
                </p>
<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            `;


        default:

            return `
<<<<<<< HEAD
                <div class="response-heading">
                    ✨ ${escapeHTML(data.name)}
=======

                <div class="response-heading">
                    ✨ ${escapeHTML(
                        data.name
                    )}
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
                </div>

                <p>
                    Information is currently unavailable.
                </p>
<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            `;

    }

}


/* =========================================================
<<<<<<< HEAD
   INTELLIGENT MAP ROUTE
=======
   GOOGLE MAPS ROUTE
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
========================================================= */

function handleRoute() {

    if (!currentPlaceData) {

        showBotMessage(
            "Please select a destination first."
        );

        return;

    }


    const name =
<<<<<<< HEAD
        currentPlaceData.name ||
        currentPlace ||
        "Destination";
=======
        currentPlaceData.name;
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


    const latitude =
        currentPlaceData.latitude;


    const longitude =
        currentPlaceData.longitude;


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    CHECK COORDINATES
    ---------------------------------------------------------
    */

    if (
        latitude === undefined ||
        latitude === null ||
        latitude === "" ||
        longitude === undefined ||
        longitude === null ||
        longitude === ""
    ) {

        showBotMessage(
            "This destination does not have valid coordinates."
        );

        return;

    }


    /*
    ---------------------------------------------------------
    CREATE INTELLIGENT MAP URL
    ---------------------------------------------------------

    Existing Intelligent Map receives:

        /map/?to=PLACE&lat=LAT&lon=LON

    ---------------------------------------------------------
    */

    const mapURL =
        "/map/" +
        "?to=" +
        encodeURIComponent(name) +
        "&lat=" +
        encodeURIComponent(latitude) +
        "&lon=" +
        encodeURIComponent(longitude);


    /*
    ---------------------------------------------------------
    CHAT RESPONSE
    ---------------------------------------------------------
    */

=======
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


>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    appendMessage(
        "bot",

        `
<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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
<<<<<<< HEAD
            Intelligent Map is ready with
            <strong>
                ${escapeHTML(name)}
            </strong>
            as your destination.
=======
            Google Maps will calculate the route
            from your current location to this destination.
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        </p>

        <button
            class="chat-route-button"
<<<<<<< HEAD
            onclick="openIntelligentMap('${escapeAttribute(mapURL)}')">

            <i class="fa-solid fa-route"></i>

            Open Intelligent Map

        </button>
        `
=======
            onclick="openGoogleMaps('${escapeAttribute(
                googleMapsURL
            )}')">

            <i class="fa-solid fa-map-location-dot"></i>

            Open in Google Maps

        </button>

        `

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    );

}


/* =========================================================
<<<<<<< HEAD
   OPEN INTELLIGENT MAP
========================================================= */

function openIntelligentMap(url) {
=======
   OPEN GOOGLE MAPS
========================================================= */

function openGoogleMaps(url) {
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    if (!url) {
        return;
    }


<<<<<<< HEAD
    window.location.href =
        url;
=======
    window.open(
        url,
        "_blank",
        "noopener,noreferrer"
    );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

}


/* =========================================================
   KEEP OLD FUNCTION NAME
<<<<<<< HEAD
   HTML MAY ALREADY USE THIS
=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    BOLD
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       BOLD
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    html =
        html.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    HEADINGS
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       HEADINGS
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    html =
        html.replace(
            /^### (.*?)$/gm,
            '<div class="response-heading">$1</div>'
        );


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    BULLET POINTS
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       BULLETS
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    html =
        html.replace(
            /^[-•]\s+(.*?)$/gm,
            "<li>$1</li>"
        );


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    NUMBERED LIST
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       NUMBERED LIST
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

    html =
        html.replace(
            /^(\d+)\.\s+(.*?)$/gm,
            "<li>$2</li>"
        );


<<<<<<< HEAD
    /*
    ---------------------------------------------------------
    LINE BREAKS
    ---------------------------------------------------------
    */
=======
    /* -----------------------------------------------------
       LINE BREAKS
    ----------------------------------------------------- */
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

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
<<<<<<< HEAD

        return null;

=======
        return null;
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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

<<<<<<< HEAD
=======

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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


<<<<<<< HEAD
    closeSidebar("left");
=======
    closeSidebar(
        "left"
    );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

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
<<<<<<< HEAD
   SET TEXT
========================================================= */

function setText(id, value) {

    const element =
        document.getElementById(id);
=======
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
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


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

<<<<<<< HEAD
}


/* =========================================================
   SEARCH FILTER
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


                        if (
                            !nameElement ||
                            !categoryElement
                        ) {

                            return;

                        }


                        const placeName =
                            nameElement.textContent
                                .toLowerCase()
                                .trim();


                        const placeCategory =
                            categoryElement.textContent
                                .toLowerCase()
                                .trim();


                        if (
                            placeName.includes(
                                searchTerm
                            )
                            ||
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
=======
}
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
