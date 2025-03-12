async function getSuggestion() {
    const interest = document.getElementById("interest").value;
    const location = await getUserLocation(); // Ensure location is correctly fetched

    if (!interest) {
        alert("Please enter an interest.");
        return;
    }

    try {
        const response = await fetch("https://your-api-url.onrender.com/get_activity_options", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ interest: interest, latitude: "40.7128", longitude: "-74.0060" }) // Replace with actual location
        });

        const data = await response.json();
        console.log("🔵 API Response:", data);  // Debugging

        if (!data.activities || !Array.isArray(data.activities)) {
            console.error("❌ API did not return expected format:", data);
            document.getElementById("activity-list").innerText = "Error fetching activities.";
            return;
        }

        // ✅ Clear previous results
        const activityContainer = document.getElementById("activity-list");
        activityContainer.innerHTML = "";  

        // ✅ Loop through activity options and display them
        data.activities.forEach((activity, index) => {
            if (activity && activity.title && activity.summary) {
                const activityElement = document.createElement("div");
                activityElement.classList.add("activity-option");
                activityElement.innerHTML = `
                    <h3>Option ${index + 1}: ${activity.title}</h3>
                    <p>${activity.summary}</p>
                `;
                activityContainer.appendChild(activityElement);
            } else {
                console.error(`❌ Missing data in activity ${index + 1}:`, activity);
            }
        });

    } catch (error) {
        console.error("🔴 Error fetching suggestion:", error);
        document.getElementById("activity-list").innerText = "Error getting suggestions. Try again.";
    }
}
