document.addEventListener("DOMContentLoaded", function() {
    const signupForm = document.getElementById('signupForm');
    signupForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(signupForm);
        const data = {};
        formData.forEach((value, key) => {data[key] = value;});

        fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                alert(data.message);
                window.location.href = '/'; 
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred. Please try again later.');
        });
    });
});
