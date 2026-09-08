// ============================================================
// GET HTML ELEMENTS
// ============================================================

<<<<<<< HEAD
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
    document.getElementById(
        "speakTranslationBtn"
    );
=======
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
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


// ============================================================
// CHECK ELEMENTS
// ============================================================

<<<<<<< HEAD
console.log(
    "Native Language AI JS loaded."
);

console.log(
    "textBox:",
    textBox
);

console.log(
    "detectBtn:",
    detectBtn
);

console.log(
    "translateBtn:",
    translateBtn
);

console.log(
    "voiceBtn:",
    voiceBtn
);

console.log(
    "speakTranslationBtn:",
    speakTranslationBtn
);
=======
console.log("Native Language AI JS loaded.");

console.log("textBox:", textBox);
console.log("detectBtn:", detectBtn);
console.log("translateBtn:", translateBtn);
console.log("voiceBtn:", voiceBtn);
console.log("speakTranslationBtn:", speakTranslationBtn);
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


// ============================================================
// CSRF TOKEN
// ============================================================

function getCSRFToken() {

<<<<<<< HEAD
    const csrfInput =
        document.querySelector(
            "#csrf-form input[name='csrfmiddlewaretoken']"
        );


    if (!csrfInput) {

        console.error(
            "CSRF token not found."
        );

        return "";

    }


    return csrfInput.value;

=======
    const csrfInput = document.querySelector(
        "#csrf-form input[name='csrfmiddlewaretoken']"
    );

    if (!csrfInput) {
        console.error("CSRF token not found.");
        return "";
    }

    return csrfInput.value;
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
}


// ============================================================
// REQUEST HEADERS
// ============================================================

function getHeaders() {

    return {
<<<<<<< HEAD

        "Content-Type":
            "application/json",

        "X-CSRFToken":
            getCSRFToken()

    };

=======
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
    };
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
}


// ============================================================
// TRANSLATION TIMER
// ============================================================

let translationTimer = null;
<<<<<<< HEAD

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
let isTranslating = false;


// ============================================================
// TRANSLATE FUNCTION
// ============================================================

async function autoTranslate() {

<<<<<<< HEAD
    if (!textBox) {
        return;
    }


    const text =
        textBox.value.trim();


    if (!text) {

        if (detectedLanguage) {

            detectedLanguage.textContent =
                "Language: Not detected";

        }


        if (englishOutput) {

            englishOutput.textContent =
                "Your translation will appear here...";

        }

        return;

=======
    const text = textBox.value.trim();

    if (!text) {

        detectedLanguage.textContent =
            "Language: Not detected";

        englishOutput.textContent =
            "Your translation will appear here...";

        return;
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    }


    if (isTranslating) {
        return;
    }


    isTranslating = true;

<<<<<<< HEAD

    if (detectedLanguage) {

        detectedLanguage.textContent =
            "Language: Detecting...";

    }


    if (englishOutput) {

        englishOutput.textContent =
            "Translating...";

    }
=======
    detectedLanguage.textContent =
        "Language: Detecting...";

    englishOutput.textContent =
        "Translating...";
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


    try {

<<<<<<< HEAD
        console.log(
            "Sending translation:",
            text
        );


        const response =
            await fetch(
                "/native/translate/",
                {

                    method: "POST",

                    headers:
                        getHeaders(),

                    credentials:
                        "same-origin",

                    body:
                        JSON.stringify({
                            text: text
                        })

                }
            );


=======
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


>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        const responseText =
            await response.text();


        console.log(
            "Translation server response:",
            responseText
        );


        let data;


        try {

<<<<<<< HEAD
            data =
                JSON.parse(
                    responseText
                );

        }

        catch (error) {
=======
            data = JSON.parse(responseText);

        } catch (error) {
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

            throw new Error(
                "Django returned invalid JSON."
            );
<<<<<<< HEAD

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        }


        // ====================================================
        // SUCCESS
        // ====================================================

<<<<<<< HEAD
        if (
            response.ok &&
            data.success
        ) {

            const sourceLanguage =
                data.detected_language ||
                data.language ||
                "Unknown";


            const targetLanguage =
                data.target_language ||
                "Translation";


            if (detectedLanguage) {

                detectedLanguage.textContent =
                    "Language: " +
                    sourceLanguage;

            }
=======
        if (response.ok && data.success) {

            detectedLanguage.textContent =
                "Language: " +
                (
                    data.detected_language ||
                    data.language ||
                    "Unknown"
                );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


            const translation =
                data.translation ||
                data.english ||
                data.result ||
                "";


<<<<<<< HEAD
            if (englishOutput) {

                englishOutput.textContent =
                    translation ||
                    "No translation returned.";

            }


            if (outputLabel) {

                outputLabel.textContent =
                    `${targetLanguage} output`;

            }


            if (targetLanguageLabel) {

                targetLanguageLabel.textContent =
                    `↔ ${sourceLanguage} → ${targetLanguage}`;

=======
            englishOutput.textContent =
                translation ||
                "No translation returned.";
            if (outputLabel) {
                outputLabel.textContent = `${data.target_language || "Translation"} output`;
            }
            if (targetLanguageLabel) {
                targetLanguageLabel.textContent = `↔ ${data.detected_language || "Source"} → ${data.target_language || "Target"}`;
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            }


            console.log(
                "Detected language:",
<<<<<<< HEAD
                sourceLanguage
=======
                data.detected_language || data.language
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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

<<<<<<< HEAD
            if (detectedLanguage) {

                detectedLanguage.textContent =
                    "Language: Error";

            }


            if (englishOutput) {

                englishOutput.textContent =
                    data.error ||
                    "Translation failed.";

            }
=======
            detectedLanguage.textContent =
                "Language: Error";


            englishOutput.textContent =
                data.error ||
                "Translation failed.";
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


            console.error(
                "Translation server error:",
                data.error
            );
<<<<<<< HEAD

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        }

    }


    catch (error) {

        console.error(
            "Translation error:",
            error
        );


<<<<<<< HEAD
        if (detectedLanguage) {

            detectedLanguage.textContent =
                "Language: Error";

        }


        if (englishOutput) {

            englishOutput.textContent =
                "Could not connect to server.";

        }

=======
        detectedLanguage.textContent =
            "Language: Error";


        englishOutput.textContent =
            "Could not connect to server.";
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
    }


    finally {

<<<<<<< HEAD
        isTranslating =
            false;

    }

=======
        isTranslating = false;

    }
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
}


// ============================================================
// AUTO TRANSLATION WHILE TYPING
// ============================================================

<<<<<<< HEAD
if (textBox) {

    textBox.addEventListener(
        "input",
        function () {

=======
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

>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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

<<<<<<< HEAD
        }
    );

}


// ============================================================
// TRANSLATE NOW BUTTON
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

if (detectBtn) {

    detectBtn.addEventListener(
        "click",
        async function () {

            if (!textBox) {
                return;
            }


            const text =
                textBox.value.trim();


            if (!text) {

                alert(
                    "Please enter some text first."
                );

                return;

            }


            if (detectedLanguage) {

                detectedLanguage.textContent =
                    "Language: Detecting...";

            }


            detectBtn.disabled =
                true;


            try {

                console.log(
                    "Sending detection:",
                    text
                );


                const response =
                    await fetch(
                        "/native/detect/",
                        {

                            method: "POST",

                            headers:
                                getHeaders(),

                            credentials:
                                "same-origin",

                            body:
                                JSON.stringify({
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

                    data =
                        JSON.parse(
                            responseText
                        );

                }

                catch (error) {

                    throw new Error(
                        "Django returned invalid detection JSON."
                    );

                }


                if (
                    response.ok &&
                    data.success
                ) {

                    if (detectedLanguage) {

                        detectedLanguage.textContent =
                            "Language: " +
                            (
                                data.language ||
                                data.detected_language ||
                                "Unknown"
                            );

                    }

                }

                else {

                    if (detectedLanguage) {

                        detectedLanguage.textContent =
                            "Language: Detection failed";

                    }


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


                if (detectedLanguage) {

                    detectedLanguage.textContent =
                        "Language: Error";

                }

            }


            finally {

                detectBtn.disabled =
                    false;

            }

        }
    );

}


// ============================================================
// 🎤 VOICE INPUT
// ============================================================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


if (!SpeechRecognition) {

    if (voiceBtn) {

        voiceBtn.disabled =
            true;

        voiceBtn.textContent =
            "🎤 Speech not supported";

    }


    console.error(
        "Speech Recognition is not supported."
    );

}

else {

    const recognition =
        new SpeechRecognition();


    // ========================================================
    // HINDI SPEECH RECOGNITION
    // ========================================================

    recognition.lang =
        "hi-IN";


    // Listen to one sentence at a time.
    recognition.continuous =
        false;


    // Show live/interim speech.
    // Interim speech is NOT sent for translation.
    recognition.interimResults =
        true;


    recognition.maxAlternatives =
        1;


    let isListening =
        false;


    // ========================================================
    // MICROPHONE BUTTON
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

                    // Make absolutely sure Hindi
                    // is selected every time.
                    recognition.lang =
                        "hi-IN";


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

    }


    // ========================================================
    // START LISTENING
    // ========================================================

    recognition.onstart =
        function () {

            isListening =
                true;


            if (voiceBtn) {

                voiceBtn.textContent =
                    "🛑 Stop Listening";


                voiceBtn.classList.add(
                    "listening"
                );

            }


            console.log(
                "Microphone started."
            );


            console.log(
                "Recognition language:",
                recognition.lang
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
                        .transcript
                        .trim();


                if (
                    event.results[i].isFinal
                ) {

                    finalText +=
                        transcript + " ";

                }

                else {

                    interimText +=
                        transcript + " ";

                }

            }


            // =================================================
            // SHOW INTERIM SPEECH ONLY
            // =================================================

            if (
                interimText.trim() &&
                !finalText.trim()
            ) {

                if (textBox) {

                    textBox.value =
                        interimText.trim();

                }

            }


            // =================================================
            // FINAL SPEECH ONLY
            // =================================================

            if (
                finalText.trim()
            ) {

                const finalSentence =
                    finalText.trim();


                if (textBox) {

                    textBox.value =
                        finalSentence;

                }


                console.log(
                    "FINAL SPEECH:",
                    finalSentence
                );


                // ------------------------------------------------
                // Do NOT translate partial/interim speech.
                // Translate only final speech.
                // ------------------------------------------------

                clearTimeout(
                    translationTimer
                );


                translationTimer =
                    setTimeout(
                        function () {

                            autoTranslate();

                        },
                        200
                    );

            }

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
        };


    // ========================================================
    // MICROPHONE END
    // ========================================================

    recognition.onend =
        function () {

<<<<<<< HEAD
            isListening =
                false;


            if (voiceBtn) {

                voiceBtn.textContent =
                    "🎤 Speak";


                voiceBtn.classList.remove(
                    "listening"
                );

            }
=======
            isListening = false;


            voiceBtn.textContent =
                "🎤 Speak";


            voiceBtn.classList.remove(
                "listening"
            );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


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


<<<<<<< HEAD
            isListening =
                false;


            if (voiceBtn) {

                voiceBtn.textContent =
                    "🎤 Speak";


                voiceBtn.classList.remove(
                    "listening"
                );

            }


            if (
                event.error ===
                "not-allowed"
            ) {

                console.error(
                    "Microphone permission denied."
                );

            }


            else if (
                event.error ===
                "no-speech"
            ) {

                console.log(
                    "No speech detected."
                );

            }


            else if (
                event.error ===
                "audio-capture"
            ) {

                console.error(
                    "No microphone was found."
                );

            }
=======
            isListening = false;


            voiceBtn.textContent =
                "🎤 Speak";


            voiceBtn.classList.remove(
                "listening"
            );
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

        };

}


// ============================================================
<<<<<<< HEAD
// 🔊 SPEAK TRANSLATION
=======
// 🔊 SPEAK ENGLISH TRANSLATION
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
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


<<<<<<< HEAD
            if (!englishOutput) {
                return;
            }


=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            const translation =
                englishOutput.textContent.trim();


            // =================================================
            // CHECK TRANSLATION
            // =================================================

            if (
                !translation ||
                translation ===
<<<<<<< HEAD
                    "Your translation will appear here..." ||
                translation ===
                    "Translating..." ||
                translation ===
                    "No translation returned."
=======
                "Your translation will appear here..." ||
                translation ===
                "Translating..." ||
                translation ===
                "No translation returned."
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            ) {

                alert(
                    "Please translate something first."
                );

                return;
<<<<<<< HEAD

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            }


            // =================================================
            // CHECK SPEECH SYNTHESIS
            // =================================================

<<<<<<< HEAD
            if (
                !(
                    "speechSynthesis"
                    in window
                )
            ) {
=======
            if (!("speechSynthesis" in window)) {
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b

                alert(
                    "Your browser does not support text-to-speech."
                );

                return;
<<<<<<< HEAD

=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            }


            // =================================================
            // STOP PREVIOUS SPEECH
            // =================================================

            window.speechSynthesis.cancel();


            // =================================================
<<<<<<< HEAD
            // DETERMINE TARGET LANGUAGE
            // =================================================

            let speechLanguage =
                "en-US";


            if (
                targetLanguageLabel &&
                targetLanguageLabel.textContent
                    .toLowerCase()
                    .includes("hindi")
            ) {

                speechLanguage =
                    "hi-IN";

            }


            // =================================================
=======
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
            // CREATE SPEECH
            // =================================================

            const speech =
                new SpeechSynthesisUtterance(
                    translation
                );


<<<<<<< HEAD
            speech.lang =
                speechLanguage;


            speech.rate =
                0.9;


            speech.pitch =
                1;


            speech.volume =
                1;
=======
            // =================================================
            // ENGLISH VOICE
            // =================================================

            speech.lang = targetLanguageLabel?.textContent.includes("Hindi") ? "hi-IN" : "en-US";

            speech.rate = 0.9;

            speech.pitch = 1;

            speech.volume = 1;
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b


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

<<<<<<< HEAD

// ============================================================
// SWAP LANGUAGE
// ============================================================

if (swapLanguageBtn) {

    swapLanguageBtn.addEventListener(
        "click",
        function () {

            if (
                !englishOutput ||
                !textBox
            ) {

                return;

            }


            const output =
                englishOutput.textContent.trim();


            if (
                !output ||
                output.includes(
                    "translation will appear"
                ) ||
                output ===
                    "Translating..."
            ) {

                return;

            }


            textBox.value =
                output;


            englishOutput.textContent =
                "Your translation will appear here...";


            if (outputLabel) {

                outputLabel.textContent =
                    "Translation";

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

=======
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
>>>>>>> b08fcca42ead610540644ffbce1a541008c4f39b
}


// ============================================================
// PAGE LOADED
// ============================================================

console.log(
    "Native Language AI is ready."
);