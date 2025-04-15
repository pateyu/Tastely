document.addEventListener("DOMContentLoaded", function () {
  const usernameForm = document.getElementById("username-form");
  const passwordForm = document.getElementById("password-form");
  const emailForm = document.getElementById("email-form");
  const securityKeyForm = document.getElementById("securityKeyForm");
  const dietForm = document.getElementById("diet-restrictions-form");
  const deleteAccountForm = document.getElementById("delete-account-form"); // Added
  const messageDisplay = document.getElementById('messageDisplay');

  usernameForm.addEventListener("submit", function (event) {
      event.preventDefault();
      submitForm(usernameForm, "/change_username");
  });

  passwordForm.addEventListener("submit", function (event) {
      event.preventDefault();
      submitForm(passwordForm, "/change_password");
  });

  emailForm.addEventListener("submit", function (event) {
      event.preventDefault();
      submitForm(emailForm, "/change_email");
  });

  securityKeyForm.addEventListener("submit", function(event) {
      event.preventDefault();
      submitForm(securityKeyForm, "/update_security_key");
  });

  dietForm.addEventListener("submit", function(event) {
      event.preventDefault();
      submitForm(dietForm, "/update_diet_restrictions");
  });
    // Added event listener for delete account form
    deleteAccountForm.addEventListener("submit", function(event) {
        event.preventDefault();
        if (confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
            deleteAccount(deleteAccountForm, "/delete_account");
        }
    });

  function submitForm(form, actionUrl) {
      const formData = new FormData(form);
      
      fetch(actionUrl, {
          method: "POST",
          body: formData,
      })
      .then(response => response.json())
      .then(data => {
          if (data.message) {
              messageDisplay.textContent = data.message;
              messageDisplay.style.color = 'green';
          } else {
              throw new Error("Unexpected response from server");
          }
      })
      .catch(error => {
          console.error("Error:", error);
          messageDisplay.textContent = "An error occurred: " + error.message;
          messageDisplay.style.color = 'red';
      });
  }

  // Function to handle delete account
  function deleteAccount(form, actionUrl) {
    fetch(actionUrl, {
        method: "POST",
        body: new FormData(form),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            messageDisplay.textContent = data.message;
            messageDisplay.style.color = 'green';
            // Redirect to logout after successful account deletion
            setTimeout(() => { window.location.href = "/logout"; }, 2000);
        } else {
            throw new Error("Unexpected response from server");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        messageDisplay.textContent = "An error occurred: " + error.message;
        messageDisplay.style.color = 'red';
    });
}

});

