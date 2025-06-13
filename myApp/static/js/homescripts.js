function exploreAuctions() {
    window.location.href = "#auctions";
}
// Function to open the login modal
function openLoginModal() {
    document.getElementById('loginModal').style.display = 'flex';
}

// Function to close the login modal
function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

// Close the modal if the user clicks outside the modal content
window.onclick = function(event) {
    if (event.target === document.getElementById('loginModal')) {
        closeLoginModal();
    }
}

// Show the details of the painting
function showDetails(paintingId) {
    const detailsBox = document.getElementById(`details-${paintingId}`);
    detailsBox.style.display = 'flex';  // Display the details box
}

// Hide the details of the painting
function hideDetails(paintingId) {
    const detailsBox = document.getElementById(`details-${paintingId}`);
    detailsBox.style.display = 'none';  // Hide the details box
}

window.onclick = function(event) {
    // Check if the clicked element is the background (not the details box itself)
    if (event.target.classList.contains('painting-details')) {
        const detailsBoxes = document.querySelectorAll('.painting-details');
        detailsBoxes.forEach(detailsBox => {
            detailsBox.style.display = 'none';
        });
    }
}

// Show the login modal when clicking "Login" button
document.getElementById('open-login').addEventListener('click', function() {
    document.getElementById('login-modal').style.display = 'flex';
});

// Show the register modal when clicking "Register here" link inside login modal
document.getElementById('register-link').addEventListener('click', function() {
    document.getElementById('login-modal').style.display = 'none';  // Hide login modal
    document.getElementById('register-modal').style.display = 'flex';  // Show register modal
});

// Show the login modal when clicking "Login here" link inside register modal
document.getElementById('login-link').addEventListener('click', function() {
    document.getElementById('register-modal').style.display = 'none';  // Hide register modal
    document.getElementById('login-modal').style.display = 'flex';  // Show login modal
});

// Close the login modal when clicking the close button
document.getElementById('close-login').addEventListener('click', function() {
    document.getElementById('login-modal').style.display = 'none';
});

// Close the register modal when clicking the close button
document.getElementById('close-register').addEventListener('click', function() {
    document.getElementById('register-modal').style.display = 'none';
});

//notification
setTimeout(() => {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => msg.style.display = 'none');
}, 10); // Hide after 5 seconds

//guest mode
document.getElementById('guestbutton').addEventListener('click', function() {
    window.location.href = '/home/'; // Adjust the URL to your guest mode view
});


document.addEventListener("DOMContentLoaded", function () {
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirm_password");

    confirmPassword.addEventListener("input", function () {
        if (password.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity("Passwords do not match.");
        } else {
            confirmPassword.setCustomValidity("");
        }
    });
});
   
    
    function redirectToAuctionDetails(paintingId) {
        const url = `/auction/upcoming/${paintingId}/`;  // Ensure the URL is correctly constructed
        window.location.href = url;
    }
    
// Timer countdown script
document.addEventListener("DOMContentLoaded", function() {
    const timers = document.querySelectorAll('.timer');

    timers.forEach(function(timer) {
        const startTime = parseInt(timer.getAttribute('data-start')); // Get the start time from the HTML attribute

        function updateTimer() {
            const now = Math.floor(Date.now() / 1000); // Current time in seconds
            const timeLeft = startTime - now; // Time remaining in seconds

            if (timeLeft <= 0) {
                timer.textContent = "Auction Started!";
                clearInterval(interval); // Stop the timer once the auction starts
            } else {
                const hours = Math.floor(timeLeft / 3600);
                const minutes = Math.floor((timeLeft % 3600) / 60);
                const seconds = timeLeft % 60;
                timer.textContent = `${hours}h ${minutes}m ${seconds}s`;
            }
        }

        // Update the timer every second
        const interval = setInterval(updateTimer, 1000);
        updateTimer(); // Run it immediately to avoid delay
    });
});
/*carousel*/

const carousel = document.querySelector('.carousel');
const prevBtn = document.querySelector('#prev-btn');
const nextBtn = document.querySelector('#next-btn');
const dots = document.querySelectorAll('.dot');

let currentIndex = 0;
const itemWidth = carousel.querySelector('.carousel-item').offsetWidth + 20; // Including margin

// Update function for active item and dot
function updateActiveItem() {
    const items = Array.from(carousel.querySelectorAll('.carousel-item'));
    
    // Loop through each item to apply transformations
    items.forEach((item, index) => {
        if (index === currentIndex) {
            item.classList.add('active');
            item.style.transform = 'scale(1.2)';
            item.style.opacity = '1';
        } else {
            item.classList.remove('active');
            item.style.transform = 'scale(0.8)';
            item.style.opacity = '0.5';
        }
    });

    // Update dots to show active state
    dots.forEach((dot, index) => {
        if (index === currentIndex) {
            dot.classList.add('active-dot');
        } else {
            dot.classList.remove('active-dot');
        }
    });

    // Enable/disable navigation buttons
    prevBtn.disabled = currentIndex === 0;
    nextBtn.disabled = currentIndex === carousel.children.length - 1;
}

// Initialize carousel state
updateActiveItem();

// Arrow button functionality
prevBtn.addEventListener('click', () => {
    if (currentIndex > 0) {
        currentIndex--;
        carousel.scrollBy({ left: -itemWidth, behavior: 'smooth' });
        updateActiveItem();
    }
});

nextBtn.addEventListener('click', () => {
    if (currentIndex < carousel.children.length - 1) {
        currentIndex++;
        carousel.scrollBy({ left: itemWidth, behavior: 'smooth' });
        updateActiveItem();
    }
});

// Dot click functionality
dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
        currentIndex = index;
        carousel.scrollTo({ left: itemWidth * currentIndex, behavior: 'smooth' });
        updateActiveItem();
    });
});

// Handle scroll events to update active item
carousel.addEventListener('scroll', () => {
    const items = Array.from(carousel.querySelectorAll('.carousel-item'));
    const centerIndex = Math.floor(items.length / 2);
    currentIndex = centerIndex;
    updateActiveItem();
});

window.addEventListener('resize', updateActiveItem);
updateActiveItem(); // Initialize active state on load

/*-carousel-*/

/*theme*/
document.getElementById('theme').addEventListener('change', function () {
    let theme = this.value;
    document.body.classList.toggle('dark-theme', theme === 'Dark');
    document.body.classList.toggle('light-theme', theme === 'Light');
    
    // Optional: Send AJAX request to save the theme in database
});
/*-theme-*/

/*timer-modal*/
// Function to open the modal and populate it with details
function showAuctionDetailsModal(auctionId) {
    // Get the modal element
    const modal = document.getElementById('auction-details-modal');
    const auctionDetails = document.getElementById('auction-details');

    // Example of dynamically populating auction details
    // Replace this with your actual data-fetching logic
    auctionDetails.innerHTML = `
        <p><strong>Auction ID:</strong> ${auctionId}</p>
            `;

    // Display the modal
    modal.style.display = 'block';
}

// Function to close the modal
function closeAuctionDetails() {
    const modal = document.getElementById('auction-details-modal');
    modal.style.display = 'none';
}
/*-timer-modal-*/


/*profile*/
document.addEventListener("DOMContentLoaded", function () {
    const profileBtn = document.querySelector(".profile-btn");
    const profileDropdown = document.querySelector(".profile-dropdown");
    const profileInitial = document.getElementById("profile-initial");
    const profilePic = document.getElementById("profile-pic");
    const profileUpload = document.getElementById("profile-upload");

    // ✅ Toggle profile dropdown when clicking the profile button
    if (profileBtn) {
        profileBtn.addEventListener("click", function (event) {
            event.stopPropagation(); // Prevent clicking from closing it immediately
            profileDropdown.classList.toggle("active");
        });
    }

    // ✅ Close dropdown when clicking outside
    document.addEventListener("click", function (event) {
        if (!profileBtn.contains(event.target) && !profileDropdown.contains(event.target)) {
            profileDropdown.classList.remove("active");
        }
    });

    // ✅ Clicking first letter opens file selection
    if (profileInitial) {
        profileInitial.addEventListener("click", function () {
            profileUpload.click();
        });
    }

    // ✅ Upload new profile image via AJAX
    profileUpload.addEventListener("change", function () {
        const file = profileUpload.files[0];
        if (file) {
            let formData = new FormData();
            formData.append("profile_image", file);

            fetch("/update-profile-picture/", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update profile image on all pages
                    if (profilePic) profilePic.src = data.profile_pic_url;
                    if (profileInitial) {
                        profileInitial.style.backgroundImage = `url(${data.profile_pic_url})`;
                        profileInitial.textContent = ""; // Remove text when image is uploaded
                    }
                } else {
                    alert("Failed to upload profile picture.");
                }
            })
            .catch(error => console.error("Error:", error));
        }
    });

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }
});

/*-profile-*/

/*folloers-following*/
function toggleFollowList(listId) {
    var list = document.getElementById(listId);
    if (list.style.display === "none") {
        list.style.display = "block";
    } else {
        list.style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const followBtn = document.getElementById("follow-btn");

    if (followBtn) {
        followBtn.addEventListener("click", function () {
            const username = followBtn.getAttribute("data-username");
            const csrfToken = document.getElementById("csrf-token").value; // Get CSRF token

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
                if (data.success) {
                    followBtn.textContent = data.following ? "Following" : "Follow";
                    followBtn.classList.toggle("following", data.following);
                    document.querySelector(".followers-count").textContent = data.followers_count;
                }
            })
            .catch(error => console.error("Error:", error));
        });
    }
});


// Function to get CSRF Token for AJAX requests
// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                return cookieValue;
            }
        }
    }
    return cookieValue;
}

/*process-effect*/
document.addEventListener("DOMContentLoaded", function () {
    const elements = document.querySelectorAll(".about, .bidding-process, .selling-process");

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("show");
            }
        });
    }, { threshold: 0.2 });

    elements.forEach(element => observer.observe(element));
});

/*-process-effect-*/

/*-followers-following-*/

/*-user-paintings-*/
/*from myApp.models import Painting
for painting in Painting.objects.all():
    print(painting.id, painting.title)*/
