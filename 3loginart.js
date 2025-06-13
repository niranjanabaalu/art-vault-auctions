
// JavaScript to handle login validation
document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevents the form from submitting

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Simple validation
    if (username === 'admin' && password === '12345') {
        alert('Login successful!');
        window.location.href = 'Art.html'; // Redirect to a dashboard or another page
    } else {
        const errorMessage = document.getElementById('error-message');
        errorMessage.style.display = 'block';
    }
});
