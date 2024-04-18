/*!
* Start Bootstrap - Landing Page v6.0.6 (https://startbootstrap.com/theme/landing-page)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-landing-page/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project


function showLoadingAnimation() {
// Display the loading animation div
document.getElementById("welcome-text").style.display = "none";
document.getElementById("loading-animation").style.display = "block";

// Wait for 3 seconds before submitting the form
setTimeout(function () {
    document.getElementById("myForm").submit(); // Submit the form
}, 10000); // 10,000 milliseconds = 10 seconds
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("loading-animation").style.display = "none";
});

function showUploadContent() {
    document.getElementById('uploadContent').style.display = 'block';
    // Add the .btn-warning class to the button with the id of 'upload_section'
    document.getElementById('upload_section').classList.add('btn-warning');
    // Remove the .btn-warning class from the button with the id of 'history_section'
    document.getElementById('history_section').classList.remove('btn-warning');
    document.getElementById('historyContent').style.display = 'none';
    // Display the form with id uploadForm
    document.getElementById('uploadForm').style.display = 'block';
}

function showHistoryContent() {
    document.getElementById('uploadContent').style.display = 'none';
    document.getElementById('historyContent').style.display = 'block';
    // Add the .btn-warning class to the button with the id of 'history_section'
    document.getElementById('history_section').classList.add('btn-warning');
    // Remove the .btn-warning class from the button with the id of 'upload_section'
    document.getElementById('upload_section').classList.remove('btn-warning');
    document.getElementById('upload_section').classList.add('btn-primary');
    // Hide the form with id uploadForm
    document.getElementById('uploadForm').style.display = 'none';

}
