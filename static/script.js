async function getSuggestion() {
    const interest = document.getElementById("interest").value;

    if (!interest) {
        alert("Please enter an interest.");
        return;
    }

    try {
        const response = await fetch("https://spontanai-backend.onrender.com/suggest", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ interest: interest })
        });

        const data = await response.json();
        document.getElementById("suggestion-output").innerText = data.suggestion || "No suggestion found.";
    } catch (error) {
        console.error("Error fetching suggestion:", error);
        document.getElementById("suggestion-output").innerText = "Error getting suggestion. Try again.";
    }
}
