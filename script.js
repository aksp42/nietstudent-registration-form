/*
  script.js - client-side validation for the Student Registration Portal.

  How it works (beginner notes):
  1. The HTML already has rules such as required, minlength and pattern.
  2. The browser checks those rules and tells us whether each field is valid.
  3. This file turns the result into a friendly message under the field.
  4. No data is sent to a server. A valid form just shows a success message.
*/
(function () {
  "use strict";

  var form = document.getElementById("registrationForm");
  if (!form) {
    return;
  }

  var statusBox = document.getElementById("formStatus");
  var resetBtn = document.getElementById("resetBtn");
  var password = document.getElementById("password");
  var confirmPassword = document.getElementById("confirmPassword");
  var dob = document.getElementById("dob");

  // Fields checked one by one (gender is handled separately below).
  var fieldIds = [
    "fullName", "email", "phone", "dob",
    "rollNumber", "course", "department", "semester",
    "address", "city", "state", "pincode",
    "password", "confirmPassword", "terms"
  ];

  var fields = fieldIds
    .map(function (id) { return document.getElementById(id); })
    .filter(function (el) { return el !== null; });

  // "required" = shown when empty, "format" = shown when the value is wrong.
  var messages = {
    fullName:        { required: "Enter your full name.", format: "Use 3 to 60 letters. Spaces, dots, apostrophes and hyphens are allowed." },
    email:           { required: "Enter your email address.", format: "Enter a valid email address, such as name@college.edu." },
    phone:           { required: "Enter your phone number.", format: "Enter exactly 10 digits, with no spaces or symbols." },
    dob:             { required: "Select your date of birth.", format: "Choose a valid date of birth that is not in the future." },
    rollNumber:      { required: "Enter your student or roll number.", format: "Use 4 to 20 letters, digits, hyphens or slashes." },
    course:          { required: "Select your course.", format: "Select your course." },
    department:      { required: "Select your department.", format: "Select your department." },
    semester:        { required: "Select your year and semester.", format: "Select your year and semester." },
    address:         { required: "Enter your street address.", format: "Enter at least 10 characters." },
    city:            { required: "Enter your city.", format: "Enter a valid city name." },
    state:           { required: "Enter your state.", format: "Enter a valid state name." },
    pincode:         { required: "Enter your PIN or ZIP code.", format: "Enter 5 or 6 digits." },
    password:        { required: "Create a password.", format: "Use 8 to 64 characters with at least one letter and one number." },
    confirmPassword: { required: "Re-enter your password.", format: "Re-enter the same password." },
    terms:           { required: "Accept the Terms and Conditions to continue.", format: "Accept the Terms and Conditions to continue." }
  };

  /* ---------- Helpers ---------- */

  function pad(number) {
    return number < 10 ? "0" + number : String(number);
  }

  // Do not allow a date of birth in the future.
  if (dob) {
    var today = new Date();
    dob.max = today.getFullYear() + "-" + pad(today.getMonth() + 1) + "-" + pad(today.getDate());
  }

  function setError(wrapper, errorBox, text) {
    if (!wrapper || !errorBox) { return; }
    errorBox.textContent = text;
    if (text) {
      wrapper.classList.add("is-invalid");
    } else {
      wrapper.classList.remove("is-invalid");
    }
  }

  function getMessage(field) {
    var v = field.validity;
    var m = messages[field.id];

    if (v.valid) { return ""; }
    if (v.customError) { return field.validationMessage; }
    if (v.valueMissing) { return m.required; }
    return m.format;
  }

  function checkPasswordMatch() {
    if (!password || !confirmPassword) { return; }
    if (confirmPassword.value !== "" && confirmPassword.value !== password.value) {
      confirmPassword.setCustomValidity("Passwords do not match.");
    } else {
      confirmPassword.setCustomValidity("");
    }
  }

  function validateField(field) {
    if (field === confirmPassword) { checkPasswordMatch(); }

    var text = getMessage(field);
    var wrapper = field.closest(".field");
    var errorBox = document.getElementById(field.id + "-error");

    setError(wrapper, errorBox, text);
    field.setAttribute("aria-invalid", text ? "true" : "false");
    return text === "";
  }

  function validateGender() {
    var chosen = form.querySelector('input[name="gender"]:checked');
    var group = document.getElementById("gender");
    if (!group) { return true; }

    var wrapper = group.closest(".field");
    var errorBox = document.getElementById("gender-error");
    setError(wrapper, errorBox, chosen ? "" : "Select your gender.");
    return Boolean(chosen);
  }

  function clearErrors() {
    var wrappers = form.querySelectorAll(".is-invalid");
    for (var i = 0; i < wrappers.length; i++) {
      wrappers[i].classList.remove("is-invalid");
    }
    var errors = form.querySelectorAll(".error");
    for (var j = 0; j < errors.length; j++) {
      errors[j].textContent = "";
    }
    for (var k = 0; k < fields.length; k++) {
      fields[k].removeAttribute("aria-invalid");
    }
    if (confirmPassword) { confirmPassword.setCustomValidity(""); }
  }

  /* ---------- Events ---------- */

  // Check a field when the user leaves it.
  form.addEventListener("focusout", function (event) {
    if (fields.indexOf(event.target) !== -1) {
      validateField(event.target);
    }
  });

  // Once a field shows an error, re-check it while the user fixes it.
  function recheck(event) {
    var target = event.target;

    if (target.name === "gender") {
      validateGender();
      return;
    }
    if (fields.indexOf(target) !== -1) {
      var wrapper = target.closest(".field");
      if (wrapper && wrapper.classList.contains("is-invalid")) {
        validateField(target);
      }
    }
    if (target === password && confirmPassword && confirmPassword.value !== "") {
      validateField(confirmPassword);
    }
  }
  form.addEventListener("input", recheck);
  form.addEventListener("change", recheck);

  // Submit: check everything, focus the first problem, or show success.
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    statusBox.hidden = true;

    var firstInvalid = null;

    for (var i = 0; i < fields.length; i++) {
      if (!validateField(fields[i]) && !firstInvalid) {
        firstInvalid = fields[i];
      }
    }

    // Gender comes after Date of birth on the page, so check its order too.
    if (!validateGender()) {
      var firstRadio = document.getElementById("genderMale");
      var genderComesFirst = !firstInvalid ||
        (firstRadio && (firstRadio.compareDocumentPosition(firstInvalid) & Node.DOCUMENT_POSITION_FOLLOWING));
      if (genderComesFirst) { firstInvalid = firstRadio; }
    }

    if (firstInvalid) {
      firstInvalid.focus();
      return;
    }

    var nameField = document.getElementById("fullName");
    var courseField = document.getElementById("course");
    var name = nameField ? nameField.value.trim() : "student";
    var course = courseField ? courseField.value : "";

    statusBox.textContent = "Registration successful. Welcome, " + name + "! Your " + course + " student profile has been created.";
    statusBox.hidden = false;

    form.reset();
    clearErrors();
    statusBox.scrollIntoView({ behavior: "smooth", block: "center" });
  });

  // Clear form: remove error messages and the success message.
  form.addEventListener("reset", function () {
    setTimeout(clearErrors, 0);
  });

  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      statusBox.hidden = true;
    });
  }
})();
