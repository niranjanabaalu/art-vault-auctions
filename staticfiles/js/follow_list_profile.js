document.addEventListener("DOMContentLoaded", function () {
    const followButtons = document.querySelectorAll(".follow-btn");
    const followersCountElement = document.getElementById("followers-count");

    followButtons.forEach(button => {
        button.addEventListener("click", function () {
            const username = this.dataset.username;
            
            fetch("/toggle-follow/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `username=${username}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "followed") {
                    this.textContent = "Following";
                } else if (data.status === "unfollowed") {
                    this.textContent = "Follow";
                }

                // ✅ Update followers count in real-time
                if (followersCountElement) {
                    followersCountElement.textContent = data.followers_count;
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });

    function getCSRFToken() {
        return document.querySelector("input[name='csrfmiddlewaretoken']").value;
    }
});
