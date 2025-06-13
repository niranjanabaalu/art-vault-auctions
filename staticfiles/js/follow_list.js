document.addEventListener("DOMContentLoaded", function () {
    console.log("Follow List JavaScript Loaded");  // Debugging Step

    document.querySelectorAll(".follow-btn").forEach(button => {
        button.addEventListener("click", function () {
            console.log("Follow button clicked for:", this.getAttribute("data-username")); // Debugging Step

            const username = this.getAttribute("data-username");
            const csrfToken = document.querySelector("#csrf-token").value;

            fetch(`/follow/${username}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                console.log("Response:", data); // Debugging Step
                if (data.success) {
                    this.textContent = data.following ? "Following" : "Follow";

                    // Update Followers Count
                    const followersCountElem = document.getElementById("followers-count");
                    if (followersCountElem) {
                        followersCountElem.textContent = data.followers_count;
                    }
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });
});
