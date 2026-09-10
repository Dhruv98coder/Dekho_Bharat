// ============================================================
// NATIVE LANGUAGE AI
// Frontend Controller
// ============================================================


// ============================================================
// GET HTML ELEMENTS
// ============================================================

const textBox =
    document.getElementById("textBox");

const detectedLanguage =
    document.getElementById("detectedLanguage");

const englishOutput =
    document.getElementById("englishOutput");

const outputLabel =
    document.getElementById("outputLabel");

const targetLanguageLabel =
    document.getElementById("targetLanguageLabel");

const swapLanguageBtn =
    document.getElementById("swapLanguageBtn");

const detectBtn =
    document.getElementById("detectBtn");

const translateBtn =
    document.getElementById("translateBtn");

const voiceBtn =
    document.getElementById("voiceBtn");

const speakTranslationBtn =
    document.getElementById("speakTranslationBtn");


// ============================================================
// INITIAL LOG
// ============================================================

console.log(
    "[NativeLanguage] JavaScript loaded."
);

console.log(
    "[NativeLanguage] textBox:",
    textBox
);

console.log(
    "[NativeLanguage] translateBtn:",
    translateBtn
);

console.log(
    "[NativeLanguage] detectBtn:",
    detectBtn
);


// ============================================================
// SAFETY CHECK
// ============================================================

if (!textBox) {

    console.error(
        "[NativeLanguage] ERROR: #textBox not found."
    );
}

if (!translateBtn) {

    console.error(
        "[NativeLanguage] ERROR: #translateBtn not found."
    );
}


// ============================================================
// CSRF TOKEN
// ============================================================

function getCSRFToken() {

    const csrfInput =
        document.querySelector(
            "#csrf-form input[name='csrfmiddlewaretoken']"
        );

    if (csrfInput) {

        return csrfInput.value;
    }

    const cookieValue =
        document.cookie
            .split("; ")
            .find(
                row =>
                    row.startsWith(
                        "csrftoken="
                    )
            );

    if (cookieValue) {

        return decodeURIComponent(
            cookieValue.split("=")[1]
        );
    }

    return "";
}


// ============================================================
// REQUEST HEADERS
// ============================================================

function getHeaders() {

    const headers = {

        "Content-Type":
            "application/json",

        "Accept":
            "application/json"

    };

    const csrfToken =
        getCSRFToken();

    if (csrfToken) {

        headers["X-CSRFToken"] =
            csrfToken;
    }

    return headers;
}


// ============================================================
// API URLS
// ============================================================

const API = {

    translate:
        "/native/translate/",

    detect:
        "/native/detect/"

};


// ============================================================
// STATE
// ============================================================

let translationTimer = null;

let isTranslating = false;

let isDetecting = false;


// ============================================================
// UI HELPERS
// ============================================================

function setTranslationStatus(
    status
) {

    if (detectedLanguage) {

        detectedLanguage.textContent =
            status;
    }
}


function setTranslationOutput(
    text
) {

    if (englishOutput) {

        englishOutput.textContent =
            text;
    }
}


function setLoadingState(
    loading
) {

    if (translateBtn) {

        translateBtn.disabled =
            loading;

        if (loading) {

            translateBtn.textContent =
                "Translating...";

        } else {

            translateBtn.textContent =
                "Translate";
        }
    }
}


// ============================================================
// SAFE JSON RESPONSE READER
// ============================================================

async function readJSONResponse(
    response
) {

    const rawText =
        await response.text();

    console.log(
        "[NativeLanguage] HTTP STATUS:",
        response.status
    );

    console.log(
        "[NativeLanguage] RESPONSE:",
        rawText
    );

    let data = null;

    try {

        data =
            JSON.parse(
                rawText
            );

    } catch (error) {

        console.error(
            "[NativeLanguage] "
            + "INVALID JSON FROM DJANGO:",
            error
        );

        throw new Error(
            `Server returned HTTP ${response.status} `
            + `but response was not valid JSON. `
            + `Response: ${rawText.substring(0, 500)}`
        );
    }

    return {

        response: response,

        data: data,

        rawText: rawText
    };
}


// ============================================================
// AUTO TRANSLATE
// ============================================================

async function autoTranslate() {

    if (!textBox) {
        return;
    }

    const text =
        textBox.value.trim();

    // --------------------------------------------------------
    // EMPTY
    // --------------------------------------------------------

    if (!text) {

        setTranslationStatus(
            "Language: Not detected"
        );

        setTranslationOutput(
            "Your translation will appear here..."
        );

        if (outputLabel) {

            outputLabel.textContent =
                "Translation output";
        }

        if (targetLanguageLabel) {

            targetLanguageLabel.textContent =
                "↔ Source → Target";
        }

        return;
    }


    // --------------------------------------------------------
    // PREVENT DUPLICATE REQUEST
    // --------------------------------------------------------

    if (isTranslating) {

        console.log(
            "[NativeLanguage] "
            + "Translation already running."
        );

        return;
    }


    isTranslating = true;

    setLoadingState(true);


    setTranslationStatus(
        "Language: Detecting..."
    );

    setTranslationOutput(
        "Translating..."
    );


    try {

        console.log(
            "========================================"
        );

        console.log(
            "[NativeLanguage] "
            + "TRANSLATION REQUEST"
        );

        console.log(
            "[NativeLanguage] TEXT:",
            text
        );


        // ====================================================
        // SEND REQUEST
        // ====================================================

        const response =
            await fetch(
                API.translate,
                {

                    method:
                        "POST",

                    headers:
                        getHeaders(),

                    credentials:
                        "same-origin",

                    cache:
                        "no-store",

                    body:
                        JSON.stringify({
                            text: text
                        })
                }
            );


        // ====================================================
        // READ RESPONSE
        // ====================================================

        const result =
            await readJSONResponse(
                response
            );

        const data =
            result.data;


        // ====================================================
        // HTTP ERROR
        // ====================================================

        if (!response.ok) {

            const backendError =
                data.error ||
                `Server returned HTTP ${response.status}.`;

            console.error(
                "[NativeLanguage] "
                + "BACKEND ERROR:",
                backendError
            );

            setTranslationStatus(
                "Language: Server Error"
            );

            setTranslationOutput(
                backendError
            );

            return;
        }


        // ====================================================
        // APPLICATION ERROR
        // ====================================================

        if (!data.success) {

            const errorMessage =
                data.error ||
                "Translation failed.";

            console.error(
                "[NativeLanguage] "
                + "APPLICATION ERROR:",
                errorMessage
            );

            setTranslationStatus(
                "Language: Translation Error"
            );

            setTranslationOutput(
                errorMessage
            );

            return;
        }


        // ====================================================
        // SUCCESS
        // ====================================================

        const language =
            data.detected_language ||
            data.language ||
            "Unknown";


        const translation =
            data.translation ||
            data.english ||
            data.result ||
            "";


        setTranslationStatus(
            "Language: " +
            language
        );


        setTranslationOutput(
            translation ||
            "No translation returned."
        );


        if (outputLabel) {

            outputLabel.textContent =
                `${
                    data.target_language ||
                    "Translation"
                } output`;
        }


        if (targetLanguageLabel) {

            targetLanguageLabel.textContent =
                `↔ ${
                    data.detected_language ||
                    "Source"
                } → ${
                    data.target_language ||
                    "Target"
                }`;
        }


        console.log(
            "[NativeLanguage] "
            + "DETECTED LANGUAGE:",
            language
        );


        console.log(
            "[NativeLanguage] "
            + "TRANSLATION:",
            translation
        );


        console.log(
            "[NativeLanguage] "
            + "TARGET LANGUAGE:",
            data.target_language
        );


        console.log(
            "========================================"
        );

    } catch (error) {

        console.error(
            "========================================"
        );

        console.error(
            "[NativeLanguage] "
            + "REQUEST FAILED:",
            error
        );

        console.error(
            "========================================"
        );


        setTranslationStatus(
            "Language: Connection Error"
        );


        // IMPORTANT:
        // Do NOT hide the real backend/network error.

        setTranslationOutput(
            error.message ||
            "Translation request failed."
        );

    } finally {

        isTranslating = false;

        setLoadingState(false);
    }
}


// ============================================================
// AUTO TRANSLATION WHILE TYPING
// ============================================================

if (textBox) {

    textBox.addEventListener(
        "input",
        function () {

            clearTimeout(
                translationTimer
            );


            translationTimer =
                setTimeout(
                    function () {

                        autoTranslate();

                    },
                    900
                );
        }
    );
}


// ============================================================
// TRANSLATE BUTTON
// ============================================================

if (translateBtn) {

    translateBtn.addEventListener(
        "click",
        function () {

            clearTimeout(
                translationTimer
            );

            autoTranslate();
        }
    );
}


// ============================================================
// DETECT LANGUAGE
// ============================================================

async function detectLanguage() {

    if (!textBox) {
        return;
    }

    const text =
        textBox.value.trim();


    if (!text) {

        setTranslationStatus(
            "Language: Not detected"
        );

        return;
    }


    if (isDetecting) {

        return;
    }


    isDetecting = true;


    if (detectBtn) {

        detectBtn.disabled =
            true;

        detectBtn.textContent =
            "Detecting...";
    }


    setTranslationStatus(
        "Language: Detecting..."
    );


    try {

        console.log(
            "[NativeLanguage] "
            + "LANGUAGE DETECTION:",
            text
        );


        const response =
            await fetch(
                API.detect,
                {

                    method:
                        "POST",

                    headers:
                        getHeaders(),

                    credentials:
                        "same-origin",

                    cache:
                        "no-store",

                    body:
                        JSON.stringify({
                            text: text
                        })
                }
            );


        const result =
            await readJSONResponse(
                response
            );


        const data =
            result.data;


        // ====================================================
        // HTTP ERROR
        // ====================================================

        if (!response.ok) {

            const errorMessage =
                data.error ||
                `Detection failed with HTTP ${response.status}.`;

            console.error(
                "[NativeLanguage] "
                + "DETECTION ERROR:",
                errorMessage
            );

            setTranslationStatus(
                "Language: Server Error"
            );

            return;
        }


        // ====================================================
        // APPLICATION ERROR
        // ====================================================

        if (!data.success) {

            setTranslationStatus(
                "Language: Detection failed"
            );

            console.error(
                "[NativeLanguage] "
                + "DETECTION FAILED:",
                data.error
            );

            return;
        }


        // ====================================================
        // SUCCESS
        // ====================================================

        const language =
            data.language ||
            data.detected_language ||
            "Unknown";


        setTranslationStatus(
            "Language: " +
            language
        );


        console.log(
            "[NativeLanguage] "
            + "DETECTED:",
            language
        );

    } catch (error) {

        console.error(
            "[NativeLanguage] "
            + "DETECTION REQUEST FAILED:",
            error
        );

        setTranslationStatus(
            "Language: Connection Error"
        );

    } finally {

        isDetecting = false;


        if (detectBtn) {

            detectBtn.disabled =
                false;

            detectBtn.textContent =
                "Detect Language";
        }
    }
}


// ============================================================
// DETECT BUTTON
// ============================================================

if (detectBtn) {

    detectBtn.addEventListener(
        "click",
        function () {

            detectLanguage();

        }
    );
}


// ============================================================
// VOICE INPUT
// ============================================================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


if (!SpeechRecognition) {

    if (voiceBtn) {

        voiceBtn.disabled =
            true;

        voiceBtn.textContent =
            "Speech not supported";
    }


    console.warn(
        "[NativeLanguage] "
        + "Speech Recognition not supported."
    );

} else {

    const recognition =
        new SpeechRecognition();


    recognition.lang =
        "hi-IN";


    recognition.continuous =
        false;


    recognition.interimResults =
        true;


    let isListening =
        false;


    // ========================================================
    // VOICE BUTTON
    // ========================================================

    if (voiceBtn) {

        voiceBtn.addEventListener(
            "click",
            function () {

                if (isListening) {

                    recognition.stop();

                    return;
                }


                try {

                    recognition.start();

                } catch (error) {

                    console.error(
                        "[NativeLanguage] "
                        + "Speech start error:",
                        error
                    );
                }
            }
        );
    }


    // ========================================================
    // SPEECH START
    // ========================================================

    recognition.onstart =
        function () {

            isListening =
                true;


            if (voiceBtn) {

                voiceBtn.textContent =
                    "Stop Listening";

                voiceBtn.classList.add(
                    "listening"
                );
            }


            console.log(
                "[NativeLanguage] "
                + "Microphone started."
            );
        };


    // ========================================================
    // SPEECH RESULT
    // ========================================================

    recognition.onresult =
        function (event) {

            let finalText =
                "";

            let interimText =
                "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                const transcript =
                    event.results[i][0]
                        .transcript;


                if (
                    event.results[i].isFinal
                ) {

                    finalText +=
                        transcript;

                } else {

                    interimText +=
                        transcript;
                }
            }


            if (textBox) {

                if (finalText) {

                    textBox.value =
                        finalText.trim();

                } else if (interimText) {

                    textBox.value =
                        interimText.trim();
                }
            }


            clearTimeout(
                translationTimer
            );


            if (finalText) {

                translationTimer =
                    setTimeout(
                        function () {

                            autoTranslate();

                        },
                        300
                    );
            }
        };


    // ========================================================
    // SPEECH END
    // ========================================================

    recognition.onend =
        function () {

            isListening =
                false;


            if (voiceBtn) {

                voiceBtn.textContent =
                    "Speak";

                voiceBtn.classList.remove(
                    "listening"
                );
            }


            console.log(
                "[NativeLanguage] "
                + "Microphone stopped."
            );
        };


    // ========================================================
    // SPEECH ERROR
    // ========================================================

    recognition.onerror =
        function (event) {

            console.error(
                "[NativeLanguage] "
                + "Speech recognition error:",
                event.error
            );


            isListening =
                false;


            if (voiceBtn) {

                voiceBtn.textContent =
                    "Speak";

                voiceBtn.classList.remove(
                    "listening"
                );
            }
        };
}


// ============================================================
// SPEAK TRANSLATION
// ============================================================

if (!speakTranslationBtn) {

    console.warn(
        "[NativeLanguage] "
        + "#speakTranslationBtn not found."
    );

} else {

    speakTranslationBtn.addEventListener(
        "click",
        function () {

            console.log(
                "[NativeLanguage] "
                + "Listen button clicked."
            );


            if (!englishOutput) {

                return;
            }


            const translation =
                englishOutput.textContent.trim();


            // =================================================
            // VALIDATION
            // =================================================

            if (
                !translation ||
                translation ===
                    "Your translation will appear here..." ||
                translation ===
                    "Translating..." ||
                translation ===
                    "No translation returned."
            ) {

                alert(
                    "Please translate something first."
                );

                return;
            }


            // =================================================
            // SPEECH SUPPORT
            // =================================================

            if (
                !(
                    "speechSynthesis"
                    in window
                )
            ) {

                alert(
                    "Text-to-speech is not supported."
                );

                return;
            }


            // =================================================
            // STOP PREVIOUS
            // =================================================

            window.speechSynthesis.cancel();


            const speech =
                new SpeechSynthesisUtterance(
                    translation
                );


            // =================================================
            // LANGUAGE
            // =================================================

            speech.lang =
                "en-US";


            speech.rate =
                0.9;

            speech.pitch =
                1;

            speech.volume =
                1;


            // =================================================
            // BUTTON
            // =================================================

            speakTranslationBtn.textContent =
                "Speaking...";


            speakTranslationBtn.disabled =
                true;


            // =================================================
            // SPEAK
            // =================================================

            speech.onend =
                function () {

                    speakTranslationBtn.textContent =
                        "Listen to Translation";

                    speakTranslationBtn.disabled =
                        false;
                };


            speech.onerror =
                function (event) {

                    console.error(
                        "[NativeLanguage] "
                        + "Speech synthesis error:",
                        event
                    );


                    speakTranslationBtn.textContent =
                        "Listen to Translation";

                    speakTranslationBtn.disabled =
                        false;
                };


            window.speechSynthesis.speak(
                speech
            );
        }
    );
}


// ============================================================
// SWAP LANGUAGE
// ============================================================

if (swapLanguageBtn) {

    swapLanguageBtn.addEventListener(
        "click",
        function () {

            if (!englishOutput) {
                return;
            }


            const output =
                englishOutput.textContent.trim();


            if (
                !output ||
                output ===
                    "Your translation will appear here..." ||
                output ===
                    "Translating..."
            ) {

                return;
            }


            textBox.value =
                output;


            setTranslationOutput(
                "Translating..."
            );


            setTranslationStatus(
                "Language: Detecting..."
            );


            if (outputLabel) {

                outputLabel.textContent =
                    "Translation output";
            }


            if (targetLanguageLabel) {

                targetLanguageLabel.textContent =
                    "↔ Direction swapped";
            }


            clearTimeout(
                translationTimer
            );


            autoTranslate();
        }
    );
}


// ============================================================
// PAGE READY
// ============================================================

console.log(
    "[NativeLanguage] "
    + "Native Language AI is ready."
);