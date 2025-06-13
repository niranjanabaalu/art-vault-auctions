document.addEventListener("DOMContentLoaded", function () {
    const followBtn = document.getElementById("follow-btn");

    if (followBtn) {
        followBtn.addEventListener("click", function () {
            const username = followBtn.getAttribute("data-username");
            let isFollowing = followBtn.getAttribute("data-following") === "true";
            const followersText = document.querySelector(".followers-count");

            fetch(`/follow/${username}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.following) {
                        followBtn.textContent = "Following";  
                        followBtn.classList.add("following");
                        followBtn.setAttribute("data-following", "true");
                    } else {
                        followBtn.textContent = "Follow";
                        followBtn.classList.remove("following");
                        followBtn.setAttribute("data-following", "false");
                    }

                    // Update count
                    followersText.textContent = data.followers_count;
                }
            })
            .catch(error => console.error("Error:", error));
        });
    }
});

// Function to get CSRF Token for AJAX requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/*user-paintings*/
// Function to open the modal
function openModal(paintingId) {
    const modal = document.getElementById('modal-' + paintingId);
    modal.style.display = 'flex';

    // Add ESC key event listener
    document.addEventListener('keydown', function escClose(event) {
        if (event.key === "Escape") {
            closeModal(paintingId);
            document.removeEventListener('keydown', escClose);
        }
    });
}

// Function to close the modal
function closeModal(paintingId) {
    const modal = document.getElementById('modal-' + paintingId);
    modal.style.display = 'none';
}

// Add event listeners to modals for closing on outside click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', function (event) {
        if (event.target === modal) {
            const paintingId = modal.getAttribute('data-painting-id');
            closeModal(paintingId);
        }
    });
});
