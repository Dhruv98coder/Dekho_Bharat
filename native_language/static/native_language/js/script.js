// ============================================================
// GET HTML ELEMENTS
// ============================================================

const textBox = document.getElementById("textBox");
const detectedLanguage = document.getElementById("detectedLanguage");
const englishOutput = document.getElementById("englishOutput");
const outputLabel = document.getElementById("outputLabel");
const targetLanguageLabel = document.getElementById("targetLanguageLabel");
const swapLanguageBtn = document.getElementById("swapLanguageBtn");

const detectBtn = document.getElementById("detectBtn");
const translateBtn = document.getElementById("translateBtn");
const voiceBtn = document.getElementById("voiceBtn");

const speakTranslationBtn =
    document.getElementById("speakTranslationBtn");


// ============================================================
// CHECK ELEMENTS
// ============================================================

console.log("Native Language AI JS loaded.");

console.log("textBox:", textBox);
console.log("detectBtn:", detectBtn);
console.log("translateBtn:", translateBtn);
console.log("voiceBtn:", voiceBtn);
console.log("speakTranslationBtn:", speakTranslationBtn);


// ============================================================
// CSRF TOKEN
// ============================================================

function getCSRFToken() {

    const csrfInput = document.querySelector(
        "#csrf-form input[name='csrfmiddlewaretoken']"
    );

    if (!csrfInput) {
        console.error("CSRF token not found.");
        return "";
    }

    return csrfInput.value;
}


// ============================================================
// REQUEST HEADERS
// ============================================================

function getHeaders() {

    return {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
    };
}


// ============================================================
// TRANSLATION TIMER
// ============================================================

let translationTimer = null;
let isTranslating = false;


// ============================================================
// TRANSLATE FUNCTION
// ============================================================

async function autoTranslate() {

    const text = textBox.value.trim();

    if (!text) {

        detectedLanguage.textContent =
            "Language: Not detected";

        englishOutput.textContent =
            "Your translation will appear here...";

        return;
    }


    if (isTranslating) {
        return;
    }


    isTranslating = true;

    detectedLanguage.textContent =
        "Language: Detecting...";

    englishOutput.textContent =
        "Translating...";


    try {

        console.log("Sending translation:", text);


        const response = await fetch(
            "/native/translate/",
            {
                method: "POST",

                headers: getHeaders(),

                credentials: "same-origin",

                body: JSON.stringify({
                    text: text
                })
            }
        );


        const responseText =
            await response.text();


        console.log(
            "Translation server response:",
            responseText
        );


        let data;


        try {

            data = JSON.parse(responseText);

        } catch (error) {

            throw new Error(
                "Django returned invalid JSON."
            );
        }


        // ====================================================
        // SUCCESS
        // ====================================================

        if (response.ok && data.success) {

            detectedLanguage.textContent =
                "Language: " +
                (
                    data.detected_language ||
                    data.language ||
                    "Unknown"
                );


            const translation =
                data.translation ||
                data.english ||
                data.result ||
                "";


            englishOutput.textContent =
                translation ||
                "No translation returned.";
            if (outputLabel) {
                outputLabel.textContent = `${data.target_language || "Translation"} output`;
            }
            if (targetLanguageLabel) {
                targetLanguageLabel.textContent = `↔ ${data.detected_language || "Source"} → ${data.target_language || "Target"}`;
            }


            console.log(
                "Detected language:",
                data.detected_language || data.language
            );


            console.log(
                "Translation:",
                translation
            );

        }


        // ====================================================
        // SERVER ERROR
        // ====================================================

        else {

            detectedLanguage.textContent =
                "Language: Error";


            englishOutput.textContent =
                data.error ||
                "Translation failed.";


            console.error(
                "Translation server error:",
                data.error
            );
        }

    }


    catch (error) {

        console.error(
            "Translation error:",
            error
        );


        detectedLanguage.textContent =
            "Language: Error";


        englishOutput.textContent =
            "Could not connect to server.";
    }


    finally {

        isTranslating = false;

    }
}


// ============================================================
// AUTO TRANSLATION WHILE TYPING
// ============================================================

textBox.addEventListener(
    "input",
    function () {

        clearTimeout(
            translationTimer
        );


        translationTimer = setTimeout(
            function () {

                autoTranslate();

            },
            800
        );

    }
);


// ============================================================
// TRANSLATE NOW BUTTON
// ============================================================

translateBtn.addEventListener(
    "click",
    function () {

        clearTimeout(
            translationTimer
        );

        autoTranslate();

    }
);


// ============================================================
// DETECT LANGUAGE
// ============================================================

detectBtn.addEventListener(
    "click",
    async function () {

        const text =
            textBox.value.trim();


        if (!text) {

            alert(
                "Please enter some text first."
            );

            return;
        }


        detectedLanguage.textContent =
            "Language: Detecting...";


        detectBtn.disabled = true;


        try {

            console.log(
                "Sending detection:",
                text
            );


            const response = await fetch(
                "/native/detect/",
                {
                    method: "POST",

                    headers: getHeaders(),

                    credentials: "same-origin",

                    body: JSON.stringify({
                        text: text
                    })
                }
            );


            const responseText =
                await response.text();


            console.log(
                "Detection server response:",
                responseText
            );


            let data;


            try {

                data = JSON.parse(responseText);

            } catch (error) {

                throw new Error(
                    "Django returned invalid detection JSON."
                );
            }


            if (
                response.ok &&
                data.success
            ) {

                detectedLanguage.textContent =
                    "Language: " +
                    (
                        data.language ||
                        data.detected_language ||
                        "Unknown"
                    );

            }

            else {

                detectedLanguage.textContent =
                    "Language: Detection failed";


                console.error(
                    "Detection error:",
                    data.error
                );

            }

        }


        catch (error) {

            console.error(
                "Detection error:",
                error
            );


            detectedLanguage.textContent =
                "Language: Error";

        }


        finally {

            detectBtn.disabled = false;

        }

    }
);


// ============================================================
// 🎤 VOICE INPUT
// ============================================================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


if (!SpeechRecognition) {

    voiceBtn.disabled = true;

    voiceBtn.textContent =
        "🎤 Speech not supported";


    console.error(
        "Speech Recognition is not supported."
    );

}


else {

    const recognition =
        new SpeechRecognition();


    recognition.lang = "hi-IN";

    recognition.continuous = false;

    recognition.interimResults = true;


    let isListening = false;


    // ========================================================
    // MICROPHONE BUTTON
    // ========================================================

    voiceBtn.addEventListener(
        "click",
        function () {

            if (isListening) {

                recognition.stop();

                return;
            }


            try {

                recognition.start();

            }

            catch (error) {

                console.error(
                    "Recognition start error:",
                    error
                );

            }

        }
    );


    // ========================================================
    // START LISTENING
    // ========================================================

    recognition.onstart =
        function () {

            isListening = true;


            voiceBtn.textContent =
                "🛑 Stop Listening";


            voiceBtn.classList.add(
                "listening"
            );


            console.log(
                "Microphone started."
            );

        };


    // ========================================================
    // SPEECH RESULT
    // ========================================================

    recognition.onresult =
        function (event) {

            let finalText = "";
            let interimText = "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                const transcript =
                    event.results[i][0].transcript;


                if (
                    event.results[i].isFinal
                ) {

                    finalText += transcript;

                }

                else {

                    interimText += transcript;

                }

            }


            // Show speech inside textbox

            if (finalText) {

                textBox.value =
                    finalText.trim();

            }

            else if (interimText) {

                textBox.value =
                    interimText.trim();

            }


            // =================================================
            // TRANSLATE SPEECH
            // =================================================

            clearTimeout(
                translationTimer
            );


            translationTimer =
                setTimeout(
                    function () {

                        autoTranslate();

                    },
                    800
                );

        };


    // ========================================================
    // MICROPHONE END
    // ========================================================

    recognition.onend =
        function () {

            isListening = false;


            voiceBtn.textContent =
                "🎤 Speak";


            voiceBtn.classList.remove(
                "listening"
            );


            console.log(
                "Microphone stopped."
            );

        };


    // ========================================================
    // MICROPHONE ERROR
    // ========================================================

    recognition.onerror =
        function (event) {

            console.error(
                "Speech recognition error:",
                event.error
            );


            isListening = false;


            voiceBtn.textContent =
                "🎤 Speak";


            voiceBtn.classList.remove(
                "listening"
            );

        };

}


// ============================================================
// 🔊 SPEAK ENGLISH TRANSLATION
// ============================================================

if (!speakTranslationBtn) {

    console.error(
        "ERROR: speakTranslationBtn was not found in HTML."
    );

}

else {

    speakTranslationBtn.addEventListener(
        "click",
        function () {

            console.log(
                "Listen button clicked."
            );


            const translation =
                englishOutput.textContent.trim();


            // =================================================
            // CHECK TRANSLATION
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
            // CHECK SPEECH SYNTHESIS
            // =================================================

            if (!("speechSynthesis" in window)) {

                alert(
                    "Your browser does not support text-to-speech."
                );

                return;
            }


            // =================================================
            // STOP PREVIOUS SPEECH
            // =================================================

            window.speechSynthesis.cancel();


            // =================================================
            // CREATE SPEECH
            // =================================================

            const speech =
                new SpeechSynthesisUtterance(
                    translation
                );


            // =================================================
            // ENGLISH VOICE
            // =================================================

            speech.lang = (targetLanguageLabel?.textContent || "").includes("Hindi") ? "hi-IN" : "en-US";

            speech.rate = 0.9;

            speech.pitch = 1;

            speech.volume = 1;


            // =================================================
            // BUTTON STATE
            // =================================================

            speakTranslationBtn.textContent =
                "🔊 Speaking...";


            speakTranslationBtn.disabled =
                true;


            // =================================================
            // SPEAK
            // =================================================

            window.speechSynthesis.speak(
                speech
            );


            // =================================================
            // SPEECH FINISHED
            // =================================================

            speech.onend =
                function () {

                    speakTranslationBtn.textContent =
                        "🔊 Listen to Translation";


                    speakTranslationBtn.disabled =
                        false;

                };


            // =================================================
            // SPEECH ERROR
            // =================================================

            speech.onerror =
                function (event) {

                    console.error(
                        "Speech synthesis error:",
                        event
                    );


                    speakTranslationBtn.textContent =
                        "🔊 Listen to Translation";


                    speakTranslationBtn.disabled =
                        false;

                };

        }
    );

}

if (swapLanguageBtn) {
    swapLanguageBtn.addEventListener("click", () => {
        const output = englishOutput.textContent.trim();
        if (!output || output.includes("translation will appear") || output === "Translating...") return;
        textBox.value = output;
        englishOutput.textContent = "Your translation will appear here...";
        if (outputLabel) outputLabel.textContent = "Translation";
        if (targetLanguageLabel) targetLanguageLabel.textContent = "↔ Direction swapped";
        autoTranslate();
    });
}


// ============================================================
// PAGE LOADED
// ============================================================

console.log(
    "Native Language AI is ready."
);