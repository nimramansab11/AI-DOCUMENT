const questionInput = document.getElementById("question");
const promptType = document.getElementById("promptType");
const topK = document.getElementById("topK");

const askButton = document.getElementById("askButton");

const answerBox = document.getElementById("answerBox");
const answerStatus = document.getElementById("answerStatus");

const sourcesContainer =
    document.getElementById("sourcesContainer");

const sourceCount =
    document.getElementById("sourceCount");

const chunkCount =
    document.getElementById("chunkCount");


// ===============================
// INITIALIZE DASHBOARD
// ===============================

document.addEventListener("DOMContentLoaded", () => {

    loadHealth();

});


// ===============================
// HEALTH CHECK
// ===============================

async function loadHealth() {

    try {

        const response = await fetch("/health");

        if (!response.ok) {
            throw new Error("Health check failed");
        }

        const data = await response.json();

        chunkCount.textContent =
            data.documents_chunks ?? "0";

    } catch (error) {

        console.error("Health error:", error);

        chunkCount.textContent = "Offline";

    }

}


// ===============================
// ASK AI
// ===============================

askButton.addEventListener("click", askQuestion);


async function askQuestion() {

    const question =
        questionInput.value.trim();

    const selectedPrompt =
        promptType.value;

    const selectedTopK =
        Number(topK.value);


    // Empty question
    if (!question) {

        questionInput.focus();

        showAnswer(
            "Please enter a question first.",
            true
        );

        return;
    }


    // Loading state
    setLoading(true);


    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                question: question,

                top_k: selectedTopK,

                prompt_type: selectedPrompt

            })

        });


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to generate answer."
            );

        }


        // Display AI answer
        showAnswer(
            data.answer,
            false
        );


        // Display retrieved sources
        displaySources(
            data.retrieved_chunks || []
        );


        answerStatus.textContent =
            formatPromptType(
                data.prompt_type
            );


    } catch (error) {

        console.error("Ask error:", error);

        showAnswer(
            error.message ||
            "Something went wrong. Please try again.",
            true
        );

        answerStatus.textContent =
            "Error";

    } finally {

        setLoading(false);

    }

}


// ===============================
// DISPLAY ANSWER
// ===============================

function showAnswer(text, isError = false) {

    answerBox.classList.remove("empty");

    answerBox.innerHTML = "";

    const content =
        document.createElement("div");

    content.textContent = text;

    content.style.whiteSpace =
        "pre-wrap";

    if (isError) {

        content.style.color =
            "#ff7b88";

    } else {

        content.style.color =
            "#d8dce5";

    }

    answerBox.appendChild(content);

}


// ===============================
// DISPLAY SOURCES
// ===============================

function displaySources(sources) {

    sourcesContainer.innerHTML = "";

    sourceCount.textContent =
        `${sources.length} source${sources.length === 1 ? "" : "s"}`;


    if (!sources.length) {

        sourcesContainer.innerHTML = `

            <div class="sources-empty">

                <span>◈</span>

                <p>
                    No relevant document chunks found.
                </p>

            </div>

        `;

        return;
    }


    sources.forEach((source, index) => {

        const card =
            document.createElement("div");

        card.className =
            "source-card";


        const distance =
            Number(source.distance);


        card.innerHTML = `

            <div class="source-top">

                <span class="source-name">
                    ${escapeHTML(source.source || "Unknown document")}
                </span>

                <span class="distance">
                    Distance: ${distance.toFixed(4)}
                </span>

            </div>


            <div class="source-meta">

                Result ${index + 1}
                • Chunk ${source.chunk ?? "—"}

            </div>


            <div class="source-content">

                ${escapeHTML(source.content || "")}

            </div>

        `;


        sourcesContainer.appendChild(card);

    });

}


// ===============================
// LOADING STATE
// ===============================

function setLoading(isLoading) {

    askButton.disabled =
        isLoading;


    if (isLoading) {

        askButton.innerHTML = `
            <span>Searching documents...</span>
            <span>◌</span>
        `;

        answerStatus.textContent =
            "Thinking";

    } else {

        askButton.innerHTML = `
            <span>Ask AI</span>
            <span>→</span>
        `;

    }

}


// ===============================
// PROMPT LABEL
// ===============================

function formatPromptType(type) {

    if (!type) {
        return "Completed";
    }

    return type
        .split("-")
        .map(word =>
            word.charAt(0).toUpperCase() +
            word.slice(1)
        )
        .join(" ");

}


// ===============================
// SECURITY
// ===============================

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


// ===============================
// ENTER KEY
// ===============================

questionInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            event.ctrlKey
        ) {

            askQuestion();

        }

    }
);