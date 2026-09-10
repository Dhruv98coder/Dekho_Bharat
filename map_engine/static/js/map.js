/* =========================================================
   GoPlan IntelligentMap - Stable Complete JS
   ========================================================= */

/* =========================================================
   MAP
   ========================================================= */

const NCR_BOUNDS = [
    [28.20, 76.65],
    [29.10, 77.85]
];

const NCR_CENTER = [28.6139, 77.2090];

const NCR_MAX_BOUNDS = [
    [28.15, 76.60],
    [29.15, 77.90]
];

const map = L.map("map", {
    zoomControl: false,
    maxBounds: NCR_MAX_BOUNDS,
    maxBoundsViscosity: 0.88,
    minZoom: 9
}).setView(NCR_CENTER, 11);

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19,
        attribution: "© OpenStreetMap contributors"
    }
).addTo(map);

L.control.zoom({
    position: "bottomright"
}).addTo(map);


/* =========================================================
   STATE
   ========================================================= */

let mode = "car";

let currentPosition = null;
let nearbyPosition = null;

let watchId = null;

let fromLocation = null;
let toLocation = null;

let routeLayers = [];
let nearbyMarkers = [];

let currentMarker = null;
let destinationMarker = null;
let navLine = null;

let activeRoute = null;
let lastRoutes = [];

let navTimer = null;
let navStepIndex = 0;
let lastSpokenStep = -1;

let searchTimer = null;
let searchController = null;

let weatherRequestSerial = 0;
let nearbyRequestSerial = 0;

let searchInProgress = false;


/* =========================================================
   API
   ========================================================= */

const API = {
    search: document.body.dataset.searchUrl,
    route: document.body.dataset.routeUrl,
    smartConnect: document.body.dataset.smartConnectUrl,
    weather: document.body.dataset.weatherUrl,
    nearby: document.body.dataset.nearbyUrl,
    awareness: document.body.dataset.awarenessUrl,
    train: document.body.dataset.trainUrl
};


/* =========================================================
   BASIC HELPERS
   ========================================================= */

function csrfToken() {
    const match = document.cookie.match(
        /(?:^|; )csrftoken=([^;]+)/
    );

    return match
        ? decodeURIComponent(match[1])
        : "";
}


function apiUrl(base, params = {}) {
    const url = new URL(base, window.location.origin);

    Object.entries(params).forEach(
        ([key, value]) => {
            if (
                value !== undefined &&
                value !== null
            ) {
                url.searchParams.set(
                    key,
                    value
                );
            }
        }
    );

    return url.toString();
}


function escapeHtml(value) {
    return String(value ?? "").replace(
        /[&<>"']/g,
        char => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        }[char])
    );
}


function validCoordinates(lat, lon) {
    lat = Number(lat);
    lon = Number(lon);

    return (
        Number.isFinite(lat) &&
        Number.isFinite(lon) &&
        lat >= -90 &&
        lat <= 90 &&
        lon >= -180 &&
        lon <= 180 &&
        !(lat === 0 && lon === 0)
    );
}


function togglePanel(id) {
    document
        .getElementById(id)
        ?.classList.toggle("hidden");
}


function closePanel(id) {
    document
        .getElementById(id)
        ?.classList.add("hidden");
}


function openMetro() {
    window.location.href = "/metro/";
}


function pinLocation(
    point,
    color = "#ef4444"
) {
    if (
        !point ||
        !validCoordinates(
            point.latitude,
            point.longitude
        )
    ) {
        return null;
    }

    return L.circleMarker(
        [
            Number(point.latitude),
            Number(point.longitude)
        ],
        {
            radius: 8,
            color: "#fff",
            weight: 3,
            fillColor: color,
            fillOpacity: 1
        }
    ).addTo(map);
}


/* =========================================================
   SEARCH BOX
   ========================================================= */

function toggleSearchBox() {

    const box =
        document.getElementById(
            "routeSearchBox"
        );

    const button =
        document.getElementById(
            "searchToggleBtn"
        );

    const text =
        document.getElementById(
            "searchToggleText"
        );

    if (!box || !button) {
        return;
    }

    const hidden =
        box.classList.toggle(
            "search-collapsed"
        );

    button.classList.toggle(
        "is-open",
        !hidden
    );

    button.setAttribute(
        "aria-expanded",
        String(!hidden)
    );

    if (text) {
        text.textContent =
            hidden
                ? "Show search"
                : "Hide search";
    }

    if (!hidden) {
        setTimeout(() => {
            document
                .getElementById("toInput")
                ?.focus();
        }, 100);
    }
}


function clearSearch() {

    const input =
        document.getElementById(
            "toInput"
        );

    const box =
        document.getElementById(
            "toSuggestions"
        );

    if (input) {
        input.value = "";
    }

    if (box) {
        box.classList.remove("show");
        box.innerHTML = "";
    }

    toLocation = null;

    if (destinationMarker) {
        map.removeLayer(
            destinationMarker
        );
        destinationMarker = null;
    }
}


function focusRouteSearch(id) {
    document
        .getElementById(id)
        ?.focus();
}


/* =========================================================
   MODE
   ========================================================= */

function setMode(newMode) {

    mode = String(
        newMode || "car"
    ).toLowerCase();

    document
        .querySelectorAll(
            ".mode,.mode-mini"
        )
        .forEach(button => {
            button.classList.toggle(
                "active",
                button.dataset.mode === mode
            );
        });

    if (mode === "train") {
        togglePanel("trainPanel");
        loadTrainSchedule();
    }
}


/* =========================================================
   NCR
   ========================================================= */

function isInsideNCR(
    lat,
    lon
) {
    lat = Number(lat);
    lon = Number(lon);

    return (
        lat >= NCR_BOUNDS[0][0] &&
        lat <= NCR_BOUNDS[1][0] &&
        lon >= NCR_BOUNDS[0][1] &&
        lon <= NCR_BOUNDS[1][1]
    );
}


/* =========================================================
   LIVE LOCATION
   ========================================================= */

function stopLiveLocation() {

    if (watchId !== null) {

        navigator.geolocation.clearWatch(
            watchId
        );

        watchId = null;
    }
}


function locateMe(force = false) {

    if (!navigator.geolocation) {

        alert(
            "Location is not supported by this browser."
        );

        return;
    }

    navigator.geolocation.getCurrentPosition(

        position => {

            const lat =
                Number(
                    position.coords.latitude
                );

            const lon =
                Number(
                    position.coords.longitude
                );

            if (
                !validCoordinates(
                    lat,
                    lon
                )
            ) {
                return;
            }

            /*
             * Current/live navigation is NCR-only.
             * Nearby does NOT use this restriction.
             */
            if (
                !isInsideNCR(
                    lat,
                    lon
                )
            ) {

                stopLiveLocation();

                if (force) {
                    alert(
                        "Live navigation is available only inside Delhi NCR."
                    );
                }

                return;
            }

            updateLocation(
                position
            );

            if (
                force &&
                currentPosition
            ) {

                setFromLocation({
                    ...currentPosition,
                    name: "Current location"
                });
            }

            map.setView(
                [lat, lon],
                15
            );
        },

        error => {

            console.warn(
                "Location error:",
                error
            );

            if (force) {
                alert(
                    "Location permission is needed."
                );
            }
        },

        {
            enableHighAccuracy: false,
            timeout: 8000,
            maximumAge: 30000
        }
    );

    if (watchId === null) {

        watchId =
            navigator.geolocation.watchPosition(

                updateLocation,

                error => {
                    console.warn(
                        "Live location error:",
                        error
                    );
                },

                {
                    enableHighAccuracy: false,
                    timeout: 10000,
                    maximumAge: 10000
                }
            );
    }
}


function updateLocation(position) {

    const lat =
        Number(
            position.coords.latitude
        );

    const lon =
        Number(
            position.coords.longitude
        );

    if (
        !validCoordinates(
            lat,
            lon
        )
    ) {
        return;
    }

    if (
        !isInsideNCR(
            lat,
            lon
        )
    ) {

        stopLiveLocation();

        if (currentMarker) {
            map.removeLayer(
                currentMarker
            );
            currentMarker = null;
        }

        currentPosition = null;

        if (
            fromLocation?.name ===
            "Current location"
        ) {

            fromLocation = null;

            const input =
                document.getElementById(
                    "fromInput"
                );

            if (input) {
                input.value = "";
            }
        }

        return;
    }

    currentPosition = {
        latitude: lat,
        longitude: lon,
        accuracy:
            Number(
                position.coords.accuracy
            ) || 999,
        speed:
            position.coords.speed,
        heading:
            position.coords.heading
    };

    if (!currentMarker) {

        currentMarker =
            L.circleMarker(
                [lat, lon],
                {
                    radius: 8,
                    color: "#fff",
                    weight: 3,
                    fillColor: "#2563eb",
                    fillOpacity: 1
                }
            )
            .addTo(map)
            .bindTooltip(
                "You"
            );

    } else {

        currentMarker.setLatLng(
            [lat, lon]
        );
    }

    const navHud =
        document.getElementById(
            "navHud"
        );

    if (
        navHud &&
        !navHud.classList.contains(
            "hidden"
        )
    ) {

        updateNavHUD();
    }
}


function useCurrentLocation() {

    if (currentPosition) {

        setFromLocation({
            ...currentPosition,
            name: "Current location"
        });

        return;
    }

    locateMe(true);
}


function setFromLocation(
    point
) {

    if (
        !point ||
        !validCoordinates(
            point.latitude,
            point.longitude
        )
    ) {
        return;
    }

    fromLocation = {
        latitude:
            Number(point.latitude),
        longitude:
            Number(point.longitude),
        name:
            point.name ||
            "Current location"
    };

    const input =
        document.getElementById(
            "fromInput"
        );

    if (input) {
        input.value =
            fromLocation.name;
    }
}


/* =========================================================
   SEARCH / GEOCODING
   ========================================================= */

async function geocodeInput(
    query,
    box,
    callback,
    remote = false
) {

    query = String(
        query || ""
    ).trim();

    if (query.length < 2) {
        callback([]);
        return;
    }

    if (
        query
            .toLowerCase()
            .includes("current location") &&
        currentPosition
    ) {

        callback([
            {
                name: "Current location",
                display_name:
                    "GPS position",
                latitude:
                    currentPosition.latitude,
                longitude:
                    currentPosition.longitude,
                source:
                    "Browser GPS"
            }
        ]);

        return;
    }

    if (searchController) {
        searchController.abort();
    }

    searchController =
        new AbortController();

    try {

        const response =
            await fetch(
                apiUrl(
                    API.search,
                    {
                        q: query,
                        remote:
                            remote
                                ? "1"
                                : "0"
                    }
                ),
                {
                    method: "GET",
                    headers: {
                        Accept:
                            "application/json"
                    },
                    signal:
                        searchController.signal
                }
            );

        if (!response.ok) {
            callback([]);
            return;
        }

        const data =
            await response.json();

        callback(
            Array.isArray(
                data.results
            )
                ? data.results
                : []
        );

    } catch (error) {

        if (
            error.name !==
            "AbortError"
        ) {

            console.warn(
                "Search failed:",
                error
            );

            callback([]);
        }
    }
}


function showResults(
    box,
    results,
    onClick
) {

    if (!box) {
        return;
    }

    if (
        !Array.isArray(results)
    ) {
        results = [];
    }

    box.innerHTML =
        results
            .map(
                (result, index) => `
                    <div
                        class="suggestion"
                        data-index="${index}"
                    >

                        <b>
                            ${escapeHtml(
                                result.name ||
                                "Place"
                            )}
                        </b>

                        <small>
                            ${escapeHtml(
                                result.display_name ||
                                result.category ||
                                "Delhi NCR"
                            )}
                        </small>

                        <em>
                            ${escapeHtml(
                                result.source ||
                                "Mapped place"
                            )}
                        </em>

                    </div>
                `
            )
            .join("")
        ||
        `
            <div class="suggestion">
                <b>No place found</b>
                <small>
                    Try a landmark, road,
                    market, station,
                    locality or city.
                </small>
            </div>
        `;

    box.classList.add(
        "show"
    );

    box
        .querySelectorAll(
            ".suggestion"
        )
        .forEach(
            (element, index) => {

                if (
                    results[index]
                ) {

                    element.onclick =
                        () => {

                            onClick(
                                results[index]
                            );

                            box.classList.remove(
                                "show"
                            );
                        };
                }
            }
        );
}


function selectPlace(
    inputId,
    result
) {

    const name =
        result.name ||
        result.display_name
            ?.split(",")[0] ||
        "Selected place";

    const point = {
        latitude:
            Number(result.latitude),
        longitude:
            Number(result.longitude),
        name:
            name
    };

    if (
        !validCoordinates(
            point.latitude,
            point.longitude
        )
    ) {
        return;
    }

    if (
        inputId ===
        "fromInput"
    ) {

        setFromLocation(
            point
        );

    } else {

        toLocation = point;

        const input =
            document.getElementById(
                "toInput"
            );

        if (input) {
            input.value =
                name;
        }

        pinDestination(
            point
        );

        map.setView(
            [
                point.latitude,
                point.longitude
            ],
            15
        );

        fetchDestinationWeather();
    }
}


function pinDestination(
    point
) {

    if (destinationMarker) {

        map.removeLayer(
            destinationMarker
        );

        destinationMarker =
            null;
    }

    destinationMarker =
        pinLocation(
            point,
            "#ef4444"
        );

    return destinationMarker;
}


/* =========================================================
   SEARCH EVENTS
   ========================================================= */

function localSearchInput(
    inputId,
    boxId
) {

    const input =
        document.getElementById(
            inputId
        );

    const box =
        document.getElementById(
            boxId
        );

    if (!input || !box) {
        return;
    }

    input.addEventListener(
        "input",
        event => {

            const query =
                event.target.value.trim();

            clearTimeout(
                searchTimer
            );

            /*
             * User changed text,
             * old location selection is no longer valid.
             */
            if (
                inputId ===
                "fromInput"
            ) {
                fromLocation = null;
            } else {
                toLocation = null;
            }

            if (
                query.length < 2
            ) {

                box.classList.remove(
                    "show"
                );

                return;
            }

            searchTimer =
                setTimeout(
                    async () => {

                        if (
                            searchInProgress
                        ) {
                            return;
                        }

                        searchInProgress =
                            true;

                        try {

                            await geocodeInput(
                                query,
                                box,
                                results => {

                                    showResults(
                                        box,
                                        results,
                                        result =>
                                            selectPlace(
                                                inputId,
                                                result
                                            )
                                    );
                                },
                                false
                            );

                        } finally {

                            searchInProgress =
                                false;
                        }
                    },
                    180
                );
        }
    );


    input.addEventListener(
        "keydown",
        event => {

            if (
                event.key !==
                "Enter"
            ) {
                return;
            }

            event.preventDefault();

            const query =
                input.value.trim();

            if (
                query.length < 2
            ) {
                return;
            }

            box.innerHTML = `
                <div class="suggestion">
                    <b>Searching...</b>
                    <small>
                        Finding the place in Delhi NCR
                    </small>
                </div>
            `;

            box.classList.add(
                "show"
            );

            geocodeInput(
                query,
                box,
                results => {

                    showResults(
                        box,
                        results,
                        result =>
                            selectPlace(
                                inputId,
                                result
                            )
                    );
                },
                true
            );
        }
    );
}


localSearchInput(
    "fromInput",
    "fromSuggestions"
);

localSearchInput(
    "toInput",
    "toSuggestions"
);


/* =========================================================
   SWAP
   ========================================================= */

function swapLocations() {

    const oldFrom =
        fromLocation;

    const oldTo =
        toLocation;

    if (oldTo) {

        setFromLocation(
            oldTo
        );

    } else {

        fromLocation = null;

        const fromInput =
            document.getElementById(
                "fromInput"
            );

        if (fromInput) {
            fromInput.value =
                "";
        }
    }

    if (oldFrom) {

        toLocation = {
            ...oldFrom
        };

        const toInput =
            document.getElementById(
                "toInput"
            );

        if (toInput) {
            toInput.value =
                oldFrom.name ||
                "Current location";
        }

        pinDestination(
            toLocation
        );

    } else {

        toLocation = null;

        const toInput =
            document.getElementById(
                "toInput"
            );

        if (toInput) {
            toInput.value =
                "";
        }
    }

    if (toLocation) {
        fetchDestinationWeather();
    }
}


/* =========================================================
   ROUTING
   ========================================================= */

function getRouteLocations() {

    if (
        !fromLocation &&
        currentPosition
    ) {

        setFromLocation({
            ...currentPosition,
            name: "Current location"
        });
    }

    return (
        fromLocation &&
        toLocation &&
        validCoordinates(
            fromLocation.latitude,
            fromLocation.longitude
        ) &&
        validCoordinates(
            toLocation.latitude,
            toLocation.longitude
        )
    );
}


function clearRoute() {

    routeLayers.forEach(
        layer => {

            try {
                map.removeLayer(
                    layer
                );
            } catch (_) {}
        }
    );

    routeLayers = [];

    if (navLine) {

        try {
            map.removeLayer(
                navLine
            );
        } catch (_) {}

        navLine = null;
    }

    activeRoute = null;
}


async function findRoute() {

    if (mode === "metro") {
        openMetro();
        return;
    }

    if (mode === "train") {
        togglePanel(
            "trainPanel"
        );
        loadTrainSchedule();
        return;
    }

    if (!getRouteLocations()) {

        alert(
            "Set both From and To."
        );

        return;
    }

    /*
     * Backend route API requires POST.
     * This is the important fix.
     */

    clearRoute();

    const button =
        document.querySelector(
            ".find-mini"
        );

    if (button) {

        button.disabled =
            true;

        button.textContent =
            "Finding...";
    }

    try {

        const response =
            await fetch(
                API.route,
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "X-CSRFToken":
                            csrfToken(),

                        "Accept":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            from: {
                                latitude:
                                    Number(
                                        fromLocation.latitude
                                    ),
                                longitude:
                                    Number(
                                        fromLocation.longitude
                                    )
                            },

                            to: {
                                latitude:
                                    Number(
                                        toLocation.latitude
                                    ),
                                longitude:
                                    Number(
                                        toLocation.longitude
                                    )
                            },

                            mode:
                                mode
                        })
                }
            );

        const data =
            await response.json();

        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                `Route failed (${response.status})`
            );
        }

        lastRoutes =
            Array.isArray(
                data.routes
            )
                ? data.routes
                : data.route
                    ? [data.route]
                    : [];

        activeRoute =
            data.route ||
            lastRoutes[0];

        if (!activeRoute) {

            throw new Error(
                "No route found."
            );
        }

        drawRoutes(
            lastRoutes
        );

        showSummary(
            activeRoute
        );

        showSteps(
            activeRoute
        );

        pinDestination(
            toLocation
        );

        document
            .getElementById(
                "routePanel"
            )
            ?.classList.remove(
                "hidden"
            );

        document
            .getElementById(
                "startNavBtn"
            )
            ?.classList.remove(
                "hidden"
            );

        if (
            activeRoute.geometry
        ) {

            const routeLayer =
                L.geoJSON(
                    activeRoute.geometry
                );

            map.fitBounds(
                routeLayer.getBounds(),
                {
                    padding:
                        [50, 100]
                }
            );
        }

        fetchAwareness();
        fetchSmartConnect();
        saveTripToHistory(
            activeRoute
        );

    } catch (error) {

        console.error(
            "Route ERROR:",
            error
        );

        alert(
            error.message ||
            "Unable to find route."
        );

    } finally {

        if (button) {

            button.disabled =
                false;

            button.textContent =
                "Find route →";
        }
    }
}


function drawRoutes(
    routes
) {

    routeLayers.forEach(
        layer => {

            try {
                map.removeLayer(
                    layer
                );
            } catch (_) {}
        }
    );

    routeLayers = [];

    if (
        !Array.isArray(routes)
    ) {
        return;
    }

    routes.forEach(
        (route, index) => {

            if (
                !route?.geometry
            ) {
                return;
            }

            const layer =
                L.geoJSON(
                    route.geometry,
                    {
                        style: {
                            weight:
                                index === 0
                                    ? 5
                                    : 3,

                            opacity:
                                index === 0
                                    ? 0.9
                                    : 0.35,

                            color:
                                index === 0
                                    ? "#2563eb"
                                    : "#64748b",

                            dashArray:
                                index === 0
                                    ? null
                                    : "7 9",

                            lineCap:
                                "round",

                            lineJoin:
                                "round"
                        }
                    }
                ).addTo(
                    map
                );

            layer.on(
                "click",
                () => {

                    activeRoute =
                        route;

                    showSummary(
                        route
                    );

                    showSteps(
                        route
                    );
                }
            );

            routeLayers.push(
                layer
            );
        }
    );
}


function selectRoute(
    index
) {

    if (
        !lastRoutes[index]
    ) {
        return;
    }

    activeRoute =
        lastRoutes[index];

    drawRoutes(
        lastRoutes
    );

    showSummary(
        activeRoute
    );

    showSteps(
        activeRoute
    );
}


function showSummary(
    route
) {

    const panel =
        document.getElementById(
            "routeSummary"
        );

    const distance =
        document.getElementById(
            "summaryDistance"
        );

    const duration =
        document.getElementById(
            "summaryDuration"
        );

    const arrival =
        document.getElementById(
            "summaryArrival"
        );

    if (panel) {
        panel.classList.remove(
            "hidden"
        );
    }

    if (distance) {
        distance.textContent =
            route.distance_text ||
            "";
    }

    if (duration) {
        duration.textContent =
            route.duration_text ||
            "";
    }

    if (arrival) {

        const minutes =
            Number(
                route.duration_minutes
            ) || 0;

        arrival.textContent =
            new Date(
                Date.now() +
                minutes * 60000
            ).toLocaleTimeString(
                [],
                {
                    hour:
                        "2-digit",
                    minute:
                        "2-digit"
                }
            );
    }

    const options =
        document.getElementById(
            "routeOptions"
        );

    if (!options) {
        return;
    }

    options.innerHTML =
        lastRoutes
            .map(
                (item, index) => `
                    <div class="route-option">

                        <span>
                            ${
                                index === 0
                                    ? "Recommended"
                                    : "Alternative " +
                                      index
                            }

                            ·

                            ${escapeHtml(
                                item.distance_text ||
                                ""
                            )}

                            ·

                            ${escapeHtml(
                                item.duration_text ||
                                ""
                            )}
                        </span>

                        <button
                            onclick="selectRoute(${index})"
                        >
                            Use
                        </button>

                    </div>
                `
            )
            .join("");
}


function showSteps(
    route
) {

    const panel =
        document.getElementById(
            "stepsPanel"
        );

    const box =
        document.getElementById(
            "routeSteps"
        );

    if (!panel || !box) {
        return;
    }

    panel.classList.remove(
        "hidden"
    );

    box.innerHTML =
        (route.steps || [])
            .map(
                (step, index) => {

                    const distance =
                        Number(
                            step.distance_m ||
                            0
                        );

                    const distanceText =
                        distance >= 1000
                            ? (
                                distance /
                                1000
                            ).toFixed(1) +
                              " km"
                            : Math.round(
                                distance
                            ) +
                              " m";

                    return `
                        <div class="step">

                            <b>
                                ${index + 1}.
                                ${escapeHtml(
                                    step.instruction ||
                                    "Continue"
                                )}
                            </b>

                            <small>
                                ${distanceText}
                                ·
                                ${Number(
                                    step.duration_min ||
                                    0
                                )} min
                            </small>

                        </div>
                    `;
                }
            )
            .join("");
}


/* =========================================================
   TRIP HISTORY
   ========================================================= */

async function saveTripToHistory(
    route
) {

    if (
        !route ||
        !toLocation
    ) {
        return;
    }

    try {

        await fetch(
            "/api/trips/",
            {
                method:
                    "POST",

                headers: {
                    "Content-Type":
                        "application/json",

                    "X-CSRFToken":
                        csrfToken()
                },

                body:
                    JSON.stringify({

                        title:
                            "Trip to " +
                            (
                                toLocation.name ||
                                "destination"
                            ),

                        origin:
                            fromLocation?.name ||
                            "Current location",

                        destination:
                            toLocation.name ||
                            "Destination",

                        mode:
                            mode,

                        distance_km:
                            route.distance_km,

                        duration_minutes:
                            route.duration_minutes,

                        details: {
                            source:
                                "intelligent-map"
                        }
                    })
            }
        );

    } catch (error) {

        console.warn(
            "Trip history error:",
            error
        );
    }
}


/* =========================================================
   NEARBY
   ========================================================= */

function clearNearbyMarkers() {

    nearbyMarkers.forEach(
        marker => {

            try {
                map.removeLayer(
                    marker
                );
            } catch (_) {}
        }
    );

    nearbyMarkers = [];
}


async function loadNearby(
    type
) {

    const box =
        document.getElementById(
            "nearbyResults"
        );

    if (!box) {
        return;
    }

    type =
        String(
            type || "tourist"
        ).toLowerCase();

    const requestId =
        ++nearbyRequestSerial;

    togglePanel(
        "nearbyPanel"
    );

    box.innerHTML = `
        <p class="muted">
            Getting your location...
        </p>
    `;

    if (!navigator.geolocation) {

        box.innerHTML = `
            <div class="result-card">
                <b>
                    Location unavailable
                </b>
                <small>
                    Your browser does not support
                    location services.
                </small>
            </div>
        `;

        return;
    }


    const processLocation =
        async position => {

            if (
                requestId !==
                nearbyRequestSerial
            ) {
                return;
            }

            const lat =
                Number(
                    position.coords?.latitude ??
                    position.latitude
                );

            const lon =
                Number(
                    position.coords?.longitude ??
                    position.longitude
                );

            if (
                !validCoordinates(
                    lat,
                    lon
                )
            ) {

                throw new Error(
                    "Invalid GPS coordinates."
                );
            }

            nearbyPosition = {
                latitude:
                    lat,
                longitude:
                    lon,
                accuracy:
                    Number(
                        position.coords?.accuracy
                    ) || 999
            };

            box.innerHTML = `
                <p class="muted">
                    Finding nearby
                    ${escapeHtml(type)}
                    within 25 km...
                </p>
            `;

            /*
             * IMPORTANT:
             * Nearby uses 25 km.
             * It does NOT use the NCR restriction.
             */
            const url =
                apiUrl(
                    API.nearby,
                    {
                        lat:
                            lat,

                        lon:
                            lon,

                        type:
                            type,

                        radius:
                            25000
                    }
                );

            console.log(
                "[Nearby] Request:",
                url
            );

            const response =
                await fetch(
                    url,
                    {
                        method:
                            "GET",

                        headers: {
                            Accept:
                                "application/json"
                        },

                        cache:
                            "no-store"
                    }
                );

            let data = {};

            try {
                data =
                    await response.json();
            } catch (error) {
                throw new Error(
                    "Nearby server returned invalid JSON."
                );
            }

            console.log(
                "[Nearby] Response:",
                data
            );

            if (
                !response.ok
            ) {
                throw new Error(
                    data.error ||
                    `Nearby HTTP ${response.status}`
                );
            }

            if (
                data.success === false &&
                data.error
            ) {
                throw new Error(
                    data.error
                );
            }

            const results =
                Array.isArray(
                    data.results
                )
                    ? data.results
                    : [];

            clearNearbyMarkers();

            if (
                !results.length
            ) {

                box.innerHTML = `
                    <div class="result-card">

                        <b>
                            No nearby
                            ${escapeHtml(type)}
                            found
                        </b>

                        <small>
                            Nothing mapped within
                            25 km of your location.
                        </small>

                        <button
                            onclick="loadNearby('${escapeHtml(type)}')"
                        >
                            Try Again
                        </button>

                    </div>
                `;

                return;
            }

            const validResults = [];

            box.innerHTML =
                results
                    .map(
                        (place) => {

                            const placeLat =
                                Number(
                                    place.latitude ??
                                    place.lat
                                );

                            const placeLon =
                                Number(
                                    place.longitude ??
                                    place.lon
                                );

                            if (
                                validCoordinates(
                                    placeLat,
                                    placeLon
                                )
                            ) {

                                validResults.push([
                                    placeLat,
                                    placeLon
                                ]);

                                const marker =
                                    L.circleMarker(
                                        [
                                            placeLat,
                                            placeLon
                                        ],
                                        {
                                            radius:
                                                7,

                                            color:
                                                "#fff",

                                            weight:
                                                2,

                                            fillColor:
                                                "#ef4444",

                                            fillOpacity:
                                                0.9
                                        }
                                    )
                                    .addTo(
                                        map
                                    )
                                    .bindTooltip(
                                        String(
                                            place.name ||
                                            "Nearby place"
                                        )
                                    );

                                nearbyMarkers.push(
                                    marker
                                );
                            }

                            const rawDistance =
                                Number(
                                    place.distance_m ??
                                    (
                                        Number(
                                            place.distance
                                        ) * 1000
                                    )
                                );

                            let distanceText =
                                "";

                            if (
                                Number.isFinite(
                                    rawDistance
                                )
                            ) {

                                distanceText =
                                    rawDistance < 1000
                                        ? `${Math.round(
                                            rawDistance
                                        )} m`
                                        : `${(
                                            rawDistance /
                                            1000
                                        ).toFixed(1)} km`;
                            }

                            const name =
                                String(
                                    place.name ||
                                    "Nearby place"
                                );

                            const safeName =
                                JSON.stringify(
                                    name
                                )
                                .replace(
                                    /</g,
                                    "\\u003c"
                                )
                                .replace(
                                    />/g,
                                    "\\u003e"
                                );

                            const hasCoordinates =
                                validCoordinates(
                                    placeLat,
                                    placeLon
                                );

                            return `
                                <div
                                    class="result-card"
                                >

                                    <b>
                                        ${escapeHtml(
                                            name
                                        )}
                                    </b>

                                    <small>
                                        ${escapeHtml(
                                            place.category ||
                                            place.type ||
                                            type
                                        )}

                                        ${
                                            distanceText
                                                ? " · " +
                                                  escapeHtml(
                                                      distanceText
                                                  )
                                                : ""
                                        }

                                        ·

                                        ${escapeHtml(
                                            place.source ||
                                            "OpenStreetMap"
                                        )}
                                    </small>

                                    ${
                                        place.address
                                            ? `
                                                <small>
                                                    ${escapeHtml(
                                                        place.address
                                                    )}
                                                </small>
                                              `
                                            : ""
                                    }

                                    ${
                                        hasCoordinates
                                            ? `
                                                <button
                                                    onclick='setDestination(
                                                        ${placeLat},
                                                        ${placeLon},
                                                        ${safeName}
                                                    )'
                                                >
                                                    Directions
                                                </button>
                                              `
                                            : ""
                                    }

                                </div>
                            `;
                        }
                    )
                    .join("");


            /*
             * Fit map around results.
             */
            if (
                validResults.length
            ) {

                const bounds =
                    L.latLngBounds(
                        validResults
                    );

                bounds.extend([
                    lat,
                    lon
                ]);

                map.fitBounds(
                    bounds,
                    {
                        padding:
                            [50, 50],
                        maxZoom:
                            14
                    }
                );
            }
        };


    try {

        /*
         * Current GPS can be used immediately.
         * This makes Nearby faster.
         */
        if (currentPosition) {

            await processLocation(
                currentPosition
            );

            return;
        }

        /*
         * Nearby gets its own GPS.
         * No NCR restriction here.
         */
        navigator.geolocation.getCurrentPosition(

            position => {

                processLocation(
                    position
                )
                .catch(
                    error => {

                        console.error(
                            "[Nearby] Search error:",
                            error
                        );

                        box.innerHTML = `
                            <div class="result-card">

                                <b>
                                    Nearby search failed
                                </b>

                                <small>
                                    ${escapeHtml(
                                        error.message ||
                                        "Server error"
                                    )}
                                </small>

                                <button
                                    onclick="loadNearby('${escapeHtml(type)}')"
                                >
                                    Try Again
                                </button>

                            </div>
                        `;
                    }
                );
            },

            error => {

                console.error(
                    "[Nearby] GPS error:",
                    error
                );

                let message =
                    "Could not get your location.";

                if (
                    error.code ===
                    1
                ) {

                    message =
                        "Location permission denied. Allow location access and try again.";

                } else if (
                    error.code ===
                    2
                ) {

                    message =
                        "Location unavailable. Check GPS/location services.";

                } else if (
                    error.code ===
                    3
                ) {

                    message =
                        "Location request timed out. Try again.";
                }

                box.innerHTML = `
                    <div class="result-card">

                        <b>
                            Location unavailable
                        </b>

                        <small>
                            ${escapeHtml(
                                message
                            )}
                        </small>

                        <button
                            onclick="loadNearby('${escapeHtml(type)}')"
                        >
                            Try Again
                        </button>

                    </div>
                `;
            },

            {
                enableHighAccuracy:
                    false,

                timeout:
                    8000,

                maximumAge:
                    60000
            }
        );

    } catch (error) {

        console.error(
            "[Nearby] ERROR:",
            error
        );

        box.innerHTML = `
            <div class="result-card">

                <b>
                    Nearby search failed
                </b>

                <small>
                    ${escapeHtml(
                        error.message ||
                        "Server error"
                    )}
                </small>

                <button
                    onclick="loadNearby('${escapeHtml(type)}')"
                >
                    Try Again
                </button>

            </div>
        `;
    }
}


/* =========================================================
   DESTINATION FROM NEARBY
   ========================================================= */

function setDestination(
    lat,
    lon,
    name
) {

    lat =
        Number(lat);

    lon =
        Number(lon);

    if (
        !validCoordinates(
            lat,
            lon
        )
    ) {

        alert(
            "Invalid destination coordinates."
        );

        return;
    }

    toLocation = {
        latitude:
            lat,

        longitude:
            lon,

        name:
            String(
                name ||
                "Destination"
            )
    };

    const input =
        document.getElementById(
            "toInput"
        );

    if (input) {
        input.value =
            toLocation.name;
    }

    pinDestination(
        toLocation
    );

    closePanel(
        "nearbyPanel"
    );

    findRoute();
}


/* =========================================================
   SMART CONNECT
   ========================================================= */

async function fetchSmartConnect() {

    const panel =
        document.getElementById(
            "smartConnect"
        );

    const body =
        document.getElementById(
            "smartConnectBody"
        );

    if (
        !panel ||
        !body ||
        !fromLocation ||
        !toLocation ||
        !activeRoute
    ) {
        return;
    }

    panel.classList.remove(
        "hidden"
    );

    body.innerHTML = `
        <div class="connect-note">
            Finding practical
            last-mile options...
        </div>
    `;

    try {

        /*
         * Current views.py expects:
         * from_lat
         * from_lon
         * to_lat
         * to_lon
         * distance_km
         */

        const response =
            await fetch(
                apiUrl(
                    API.smartConnect,
                    {
                        from_lat:
                            fromLocation.latitude,

                        from_lon:
                            fromLocation.longitude,

                        to_lat:
                            toLocation.latitude,

                        to_lon:
                            toLocation.longitude,

                        distance_km:
                            activeRoute.distance_km ||
                            1
                    }
                )
            );

        const data =
            await response.json();

        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Smart Connect unavailable."
            );
        }

        const origin =
            data.origin_stop ||
            {};

        const destination =
            data.destination_stop ||
            {};

        body.innerHTML = `

            <div class="connect-leg">

                <div class="connect-icon">
                    🛺
                </div>

                <div class="connect-copy">

                    <b>
                        Auto pickup →
                        ${escapeHtml(
                            origin.name ||
                            "nearest bus stop"
                        )}
                    </b>

                    <span>
                        ${
                            origin.distance_m
                                ? `${origin.distance_m} m from start`
                                : "Nearby pickup point"
                        }
                    </span>

                </div>

                <div class="connect-fare">
                    ₹${Number(
                        data.auto_fare ||
                        0
                    )}
                </div>

            </div>


            <div class="connect-leg">

                <div class="connect-icon">
                    🚌
                </div>

                <div class="connect-copy">

                    <b>
                        Bus →
                        ${escapeHtml(
                            destination.name ||
                            "destination-side stop"
                        )}
                    </b>

                    <span>
                        ${escapeHtml(
                            data.bus_text ||
                            "Estimated bus leg"
                        )}
                    </span>

                </div>

                <div class="connect-fare">
                    ₹${Number(
                        data.bus_fare ||
                        0
                    )}
                </div>

            </div>


            <div class="connect-leg">

                <div class="connect-icon">
                    🚶
                </div>

                <div class="connect-copy">

                    <b>
                        Walk →
                        final destination
                    </b>

                    <span>
                        Short final walk
                    </span>

                </div>

                <div class="connect-fare">
                    Free
                </div>

            </div>


            <div class="connect-total">

                <span>
                    Estimated total
                </span>

                <b>
                    ₹${Number(
                        data.total_fare ||
                        0
                    )}
                    ·
                    ${escapeHtml(
                        data.total_time_text ||
                        ""
                    )}
                </b>

            </div>

            <div class="connect-note">
                Bus route and fare are estimates.
                No live bus departure is claimed.
            </div>
        `;

    } catch (error) {

        console.warn(
            "Smart Connect error:",
            error
        );

        body.innerHTML = `
            <div class="connect-note">
                Smart Connect is unavailable right now.
                You can still use the main route.
            </div>
        `;
    }
}


/* =========================================================
   WEATHER
   ========================================================= */

async function fetchWeather(
    lat,
    lon
) {

    if (
        !validCoordinates(
            lat,
            lon
        )
    ) {
        return;
    }

    const requestId =
        ++weatherRequestSerial;

    try {

        const response =
            await fetch(
                apiUrl(
                    API.weather,
                    {
                        lat:
                            Number(lat),
                        lon:
                            Number(lon)
                    }
                ),
                {
                    cache:
                        "no-store"
                }
            );

        if (!response.ok) {
            return;
        }

        const data =
            await response.json();

        if (
            requestId !==
            weatherRequestSerial ||
            data.error
        ) {
            return;
        }

        renderWeather(
            data,
            "Your current location"
        );

    } catch (error) {

        console.warn(
            "Weather error:",
            error
        );
    }
}


async function fetchDestinationWeather() {

    if (
        !toLocation ||
        !validCoordinates(
            toLocation.latitude,
            toLocation.longitude
        )
    ) {
        return;
    }

    const requestId =
        ++weatherRequestSerial;

    try {

        const response =
            await fetch(
                apiUrl(
                    API.weather,
                    {
                        lat:
                            Number(
                                toLocation.latitude
                            ),

                        lon:
                            Number(
                                toLocation.longitude
                            )
                    }
                ),
                {
                    cache:
                        "no-store"
                }
            );

        if (!response.ok) {
            return;
        }

        const data =
            await response.json();

        if (
            requestId !==
            weatherRequestSerial ||
            data.error
        ) {
            return;
        }

        const current =
            data.current ||
            {};

        const rain =
            data.daily
                ?.precipitation_probability_max
                ?.[0] ??
            0;

        const weatherPlace =
            toLocation.name ||
            "Destination";

        const destinationText =
            document.getElementById(
                "destinationWeatherText"
            );

        if (destinationText) {

            destinationText.textContent =
                `${weatherPlace}: ` +
                `${Math.round(
                    current.temperature_2m ??
                    0
                )}° · ` +
                `${weatherText(
                    current.weather_code
                )} · ` +
                `rain ${rain}% today.`;
        }

    } catch (error) {

        console.warn(
            "Destination weather error:",
            error
        );
    }
}


function renderWeather(
    data,
    place
) {

    const current =
        data.current ||
        {};

    const rain =
        data.daily
            ?.precipitation_probability_max
            ?.[0] ??
        0;

    const temp =
        document.getElementById(
            "weatherTemp"
        );

    const text =
        document.getElementById(
            "weatherText"
        );

    const feels =
        document.getElementById(
            "weatherFeels"
        );

    const rainBox =
        document.getElementById(
            "weatherRain"
        );

    const wind =
        document.getElementById(
            "weatherWind"
        );

    const icon =
        document.getElementById(
            "weatherIcon"
        );

    const location =
        document.getElementById(
            "weatherPlace"
        );

    if (temp) {

        temp.textContent =
            Math.round(
                current.temperature_2m ??
                0
            ) + "°";
    }

    if (text) {

        text.textContent =
            weatherText(
                current.weather_code
            );
    }

    if (feels) {

        feels.textContent =
            Math.round(
                current.apparent_temperature ??
                current.temperature_2m ??
                0
            ) + "°";
    }

    if (rainBox) {

        rainBox.textContent =
            rain + "%";
    }

    if (wind) {

        wind.textContent =
            Math.round(
                current.wind_speed_10m ??
                0
            ) +
            " km/h";
    }

    if (icon) {

        icon.textContent =
            weatherEmoji(
                current.weather_code
            );
    }

    if (location) {

        location.textContent =
            place;
    }

    renderForecast(
        data.daily
    );

    renderTips(
        current
    );
}


function weatherText(
    code
) {

    if (code === 0) {
        return "Clear sky";
    }

    if (
        [1, 2, 3].includes(
            code
        )
    ) {
        return "Partly cloudy";
    }

    if (
        [45, 48].includes(
            code
        )
    ) {
        return "Hazy / foggy";
    }

    if (
        [
            51, 53, 55,
            61, 63, 65,
            80, 81, 82
        ].includes(code)
    ) {
        return "Rain likely";
    }

    if (
        [95, 96, 99].includes(
            code
        )
    ) {
        return "Thunderstorm";
    }

    return "Mixed conditions";
}


function weatherEmoji(
    code
) {

    if (code === 0) {
        return "☀️";
    }

    if (
        [1, 2, 3].includes(
            code
        )
    ) {
        return "⛅";
    }

    if (
        [45, 48].includes(
            code
        )
    ) {
        return "🌫️";
    }

    if (
        [
            51, 53, 55,
            61, 63, 65,
            80, 81, 82
        ].includes(code)
    ) {
        return "🌧️";
    }

    if (
        [95, 96, 99].includes(
            code
        )
    ) {
        return "⛈️";
    }

    return "🌤️";
}


function renderForecast(
    daily
) {

    const box =
        document.getElementById(
            "forecast"
        );

    if (
        !box ||
        !daily?.time
    ) {
        return;
    }

    box.innerHTML =
        daily.time
            .map(
                (date, index) => {

                    const code =
                        daily
                            .weather_code
                            ?.[index] ??
                        0;

                    const rain =
                        daily
                            .precipitation_probability_max
                            ?.[index] ??
                        0;

                    return `
                        <div class="day">

                            <b>
                                ${new Date(
                                    date
                                ).toLocaleDateString(
                                    [],
                                    {
                                        weekday:
                                            "short"
                                    }
                                )}
                            </b>

                            <span>
                                ${weatherEmoji(
                                    code
                                )}
                            </span>

                            <small>
                                ${Math.round(
                                    daily
                                        .temperature_2m_max
                                        ?.[index] ??
                                    0
                                )}°
                                /
                                ${Math.round(
                                    daily
                                        .temperature_2m_min
                                        ?.[index] ??
                                    0
                                )}°
                            </small>

                            <small>
                                Rain ${rain}%
                            </small>

                        </div>
                    `;
                }
            )
            .join("");
}


function renderTips(
    current
) {

    const box =
        document.getElementById(
            "weatherTips"
        );

    if (!box) {
        return;
    }

    const tips = [];

    if (
        Number(
            current.precipitation
        ) > 0 ||
        Number(
            current.weather_code
        ) >= 51
    ) {

        tips.push(
            "Rain-aware: allow extra travel time."
        );
    }

    if (
        Number(
            current.wind_speed_10m
        ) > 30
    ) {

        tips.push(
            "Wind is elevated: take extra care."
        );
    }

    tips.push(
        mode === "foot"
            ? "Walking: use crossings and sidewalks."
            : mode === "bike"
                ? "Bike: stay visible and ride safely."
                : "Drive safely and use voice guidance."
    );

    box.innerHTML =
        tips
            .map(
                tip => `
                    <div class="tip">
                        ✦ ${escapeHtml(
                            tip
                        )}
                    </div>
                `
            )
            .join("");
}


function toggleWeather() {

    togglePanel(
        "weatherPanel"
    );

    if (currentPosition) {

        fetchWeather(
            currentPosition.latitude,
            currentPosition.longitude
        );

    } else {

        /*
         * Do not generate weather request
         * with 0,0 or fake coordinates.
         */
        locateMe(
            false
        );
    }

    if (toLocation) {
        fetchDestinationWeather();
    }
}


/* =========================================================
   AWARENESS
   ========================================================= */

async function fetchAwareness() {

    try {

        const response =
            await fetch(
                apiUrl(
                    API.awareness,
                    {
                        mode:
                            mode
                    }
                )
            );

        if (!response.ok) {
            return;
        }

        const data =
            await response.json();

        const box =
            document.getElementById(
                "awarenessText"
            );

        if (box) {

            box.textContent =
                data.tips?.[0] ||
                "Stay aware while travelling.";
        }

    } catch (error) {

        console.warn(
            "Awareness error:",
            error
        );
    }
}


/* =========================================================
   TRAIN
   ========================================================= */

async function loadTrainSchedule() {

    const box =
        document.getElementById(
            "trainSchedule"
        );

    if (!box) {
        return;
    }

    try {

        const response =
            await fetch(
                API.train
            );

        if (!response.ok) {
            throw new Error(
                "Train request failed"
            );
        }

        const data =
            await response.json();

        box.innerHTML =
            (data.slots || [])
                .map(
                    slot => `
                        <div class="slot">

                            <b>
                                ${escapeHtml(
                                    slot.label
                                )}
                            </b>

                            <span>
                                ${escapeHtml(
                                    slot.time
                                )}
                            </span>

                            <small>
                                ${escapeHtml(
                                    slot.note
                                )}
                            </small>

                        </div>
                    `
                )
                .join("");

    } catch (error) {

        console.warn(
            "Train schedule error:",
            error
        );

        box.innerHTML = `
            <div class="slot">
                Train schedule unavailable.
            </div>
        `;
    }
}


/* =========================================================
   NAVIGATION
   ========================================================= */

function haversine(
    lat1,
    lon1,
    lat2,
    lon2
) {

    const R = 6371;
    const p = Math.PI / 180;

    const dLat =
        (lat2 - lat1) * p;

    const dLon =
        (lon2 - lon1) * p;

    const a =
        Math.sin(
            dLat / 2
        ) ** 2
        +
        Math.cos(
            lat1 * p
        )
        *
        Math.cos(
            lat2 * p
        )
        *
        Math.sin(
            dLon / 2
        ) ** 2;

    return (
        2 *
        R *
        Math.asin(
            Math.sqrt(a)
        )
    );
}


function nearestPointOnRoute(
    route,
    lat,
    lon
) {

    const coordinates =
        route?.geometry?.coordinates ||
        [];

    if (
        coordinates.length < 2
    ) {
        return null;
    }

    let best = {
        distance:
            Infinity,

        index:
            0,

        lat:
            coordinates[0][1],

        lon:
            coordinates[0][0]
    };

    for (
        let i = 0;
        i < coordinates.length - 1;
        i++
    ) {

        const point =
            coordinates[i];

        const next =
            coordinates[i + 1];

        const d =
            haversine(
                lat,
                lon,
                point[1],
                point[0]
            );

        if (
            d <
            best.distance
        ) {

            best = {
                distance:
                    d,

                index:
                    i,

                lat:
                    point[1],

                lon:
                    point[0]
            };
        }

        const d2 =
            haversine(
                lat,
                lon,
                next[1],
                next[0]
            );

        if (
            d2 <
            best.distance
        ) {

            best = {
                distance:
                    d2,

                index:
                    i,

                lat:
                    next[1],

                lon:
                    next[0]
            };
        }
    }

    return best;
}


function remainingRouteGeometry(
    route,
    lat,
    lon
) {

    if (
        !route?.geometry
    ) {
        return null;
    }

    const coordinates =
        route.geometry.coordinates;

    if (
        !coordinates ||
        coordinates.length < 2
    ) {
        return route.geometry;
    }

    const nearest =
        nearestPointOnRoute(
            route,
            lat,
            lon
        );

    if (!nearest) {
        return route.geometry;
    }

    return {
        type:
            "LineString",

        coordinates: [
            [
                nearest.lon,
                nearest.lat
            ],
            ...coordinates.slice(
                nearest.index + 1
            )
        ]
    };
}


function startNavigation() {

    if (!currentPosition) {

        locateMe(
            true
        );

        setTimeout(
            () => {
                if (currentPosition) {
                    startNavigation();
                }
            },
            1500
        );

        return;
    }

    if (!activeRoute) {

        alert(
            "Find a route first."
        );

        return;
    }

    const hud =
        document.getElementById(
            "navHud"
        );

    if (hud) {
        hud.classList.remove(
            "hidden"
        );
    }

    const destination =
        document.getElementById(
            "navDestination"
        );

    if (destination) {
        destination.textContent =
            toLocation?.name ||
            "Destination";
    }

    navStepIndex = 0;
    lastSpokenStep = -1;

    updateNavHUD();

    if (navTimer) {
        clearInterval(
            navTimer
        );
    }

    navTimer =
        setInterval(
            () => {

                updateNavHUD();
                speakNextManeuver();

            },
            3000
        );

    speakNextManeuver();
}


function stopNavigation() {

    document
        .getElementById(
            "navHud"
        )
        ?.classList.add(
            "hidden"
        );

    if (navTimer) {

        clearInterval(
            navTimer
        );

        navTimer = null;
    }

    speechStop();

    if (navLine) {

        try {
            map.removeLayer(
                navLine
            );
        } catch (_) {}

        navLine = null;
    }
}


function recenterNavigation() {

    if (!currentPosition) {
        return;
    }

    map.setView(
        [
            currentPosition.latitude,
            currentPosition.longitude
        ],
        17,
        {
            animate:
                true
        }
    );
}


function updateNavHUD() {

    if (
        !currentPosition ||
        !toLocation ||
        !activeRoute
    ) {
        return;
    }

    const distance =
        haversine(
            currentPosition.latitude,
            currentPosition.longitude,
            toLocation.latitude,
            toLocation.longitude
        );

    const remaining =
        document.getElementById(
            "navRemaining"
        );

    if (remaining) {

        remaining.textContent =
            distance < 1
                ? Math.round(
                    distance * 1000
                ) +
                  " m"
                : distance.toFixed(
                    1
                ) +
                  " km";
    }

    const speed =
        document.getElementById(
            "navSpeed"
        );

    if (speed) {

        speed.textContent =
            currentPosition.speed
                ? Math.round(
                    currentPosition.speed *
                    3.6
                )
                : "0";
    }

    const eta =
        document.getElementById(
            "navEta"
        );

    if (eta) {

        /*
         * Use route duration.
         * It is more stable than calculating
         * from straight-line GPS distance.
         */
        const minutes =
            Number(
                activeRoute.duration_minutes ||
                0
            );

        eta.textContent =
            new Date(
                Date.now() +
                minutes * 60000
            ).toLocaleTimeString(
                [],
                {
                    hour:
                        "2-digit",
                    minute:
                        "2-digit"
                }
            );
    }

    const geometry =
        remainingRouteGeometry(
            activeRoute,
            currentPosition.latitude,
            currentPosition.longitude
        );

    if (geometry) {

        if (navLine) {

            try {
                map.removeLayer(
                    navLine
                );
            } catch (_) {}
        }

        navLine =
            L.geoJSON(
                geometry,
                {
                    style: {
                        color:
                            "#2563eb",

                        weight:
                            4,

                        opacity:
                            0.85,

                        lineCap:
                            "round",

                        lineJoin:
                            "round"
                    }
                }
            ).addTo(map);
    }
}


function speakNextManeuver() {

    if (
        !activeRoute ||
        !activeRoute.steps?.length ||
        !currentPosition
    ) {
        return;
    }

    /*
     * Find the nearest useful next step.
     */
    let bestIndex =
        Math.min(
            navStepIndex,
            activeRoute.steps.length - 1
        );

    let bestDistance =
        Infinity;

    for (
        let i =
            Math.max(
                0,
                navStepIndex
            );

        i <
        activeRoute.steps.length;

        i++
    ) {

        const step =
            activeRoute.steps[i];

        const location =
            step.location ||
            [];

        if (
            location.length <
            2
        ) {
            continue;
        }

        const distance =
            haversine(
                currentPosition.latitude,
                currentPosition.longitude,
                Number(location[0]),
                Number(location[1])
            );

        if (
            distance <
            bestDistance
        ) {

            bestDistance =
                distance;

            bestIndex =
                i;
        }
    }

    navStepIndex =
        bestIndex;

    const step =
        activeRoute.steps[
            bestIndex
        ];

    const instruction =
        document.getElementById(
            "navInstruction"
        );

    if (instruction) {

        instruction.textContent =
            step?.instruction ||
            "Follow the highlighted route.";
    }

    const awareness =
        document.getElementById(
            "awarenessText"
        );

    if (awareness) {

        awareness.textContent =
            step?.instruction ||
            "Stay aware while travelling.";
    }

    /*
     * Speak only when close to maneuver.
     */
    if (
        step &&
        bestDistance <= 0.12 &&
        bestIndex !== lastSpokenStep
    ) {

        lastSpokenStep =
            bestIndex;

        speakText(
            step.instruction ||
            "Continue on the route."
        );
    }
}


/* =========================================================
   VOICE
   ========================================================= */

function speakText(
    text
) {

    if (
        !("speechSynthesis" in window)
    ) {
        return;
    }

    speechSynthesis.cancel();

    const utterance =
        new SpeechSynthesisUtterance(
            String(text || "")
        );

    utterance.rate =
        0.95;

    utterance.pitch =
        1;

    utterance.volume =
        1;

    utterance.onstart =
        () =>
            setListenState(
                true
            );

    utterance.onend =
        () =>
            setListenState(
                false
            );

    utterance.onerror =
        () =>
            setListenState(
                false
            );

    speechSynthesis.speak(
        utterance
    );
}


function speechStop() {

    if (
        "speechSynthesis" in window
    ) {
        speechSynthesis.cancel();
    }

    setListenState(
        false
    );
}


function toggleSpeech() {

    if (
        "speechSynthesis" in window &&
        speechSynthesis.speaking
    ) {

        speechStop();

        return;
    }

    const place =
        document.getElementById(
            "weatherPlace"
        )?.innerText ||
        "your location";

    const temperature =
        document.getElementById(
            "weatherTemp"
        )?.innerText ||
        "";

    const summary =
        document.getElementById(
            "weatherText"
        )?.innerText ||
        "";

    const destination =
        document.getElementById(
            "destinationWeatherText"
        )?.innerText ||
        "";

    const forecast =
        [
            ...document.querySelectorAll(
                "#forecast .day"
            )
        ]
        .map(
            item =>
                item.innerText.replace(
                    /\n/g,
                    " "
                )
        )
        .join(". ");

    speakText(
        `GoPlan weather for ${place}. ` +
        `It is ${temperature}, ${summary}. ` +
        `${destination}. ` +
        `Seven day forecast: ${forecast}`
    );
}


function setListenState(
    active
) {

    const button =
        document.getElementById(
            "listenBtn"
        );

    const text =
        document.getElementById(
            "listenText"
        );

    if (!button) {
        return;
    }

    button.classList.toggle(
        "speaking",
        active
    );

    if (text) {

        text.textContent =
            active
                ? "Stop"
                : "Listen";
    }

    const icon =
        button.querySelector(
            "span"
        );

    if (icon) {

        icon.textContent =
            active
                ? "■"
                : "🔊";
    }
}


/* =========================================================
   INITIALIZATION
   ========================================================= */

/*
 * Do NOT call locateMe() automatically.
 *
 * This avoids:
 *     /weather/?lat=0&lon=0
 *
 * and avoids unnecessarily asking for
 * location permission when the map opens.
 */

loadTrainSchedule();

setTimeout(
    () => {
        map.invalidateSize();
    },
    400
);


/* =========================================================
   DEEP LINK
   ========================================================= */

(function initGoPlanDeepLink() {

    const params =
        new URLSearchParams(
            window.location.search
        );

    const destinationName =
        params.get("to");

    const lat =
        Number(
            params.get("lat")
        );

    const lon =
        Number(
            params.get("lon")
        );

    if (destinationName) {

        const input =
            document.getElementById(
                "toInput"
            );

        if (input) {
            input.value =
                destinationName;
        }
    }

    if (
        validCoordinates(
            lat,
            lon
        )
    ) {

        const point = {
            latitude:
                lat,

            longitude:
                lon,

            name:
                destinationName ||
                "Destination"
        };

        toLocation =
            point;

        pinDestination(
            point
        );

        map.setView(
            [lat, lon],
            15
        );

        fetchDestinationWeather();

        return;
    }

    /*
     * Deep link without coordinates:
     * use normal search after page is ready.
     */
    if (destinationName) {

        setTimeout(
            () => {

                const box =
                    document.getElementById(
                        "toSuggestions"
                    );

                geocodeInput(
                    destinationName,
                    box,
                    results => {

                        if (
                            results?.length
                        ) {

                            selectPlace(
                                "toInput",
                                results[0]
                            );
                        }
                    },
                    true
                );

            },
            400
        );
    }

})();