document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("loginForm");
  loginForm.addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission
    const formData = new FormData(loginForm);
    const data = {
      username: formData.get("username"),
      password: formData.get("password"),
    };

    fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json()) // Parse JSON response
      .then((data) => {
        if (data.message === "Login successful") {
          window.location.href = data.redirect; // Redirect on successful login
        } else {
          alert("Login failed. Please check your username and password.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred. Please try again later.");
      });
  });
});
