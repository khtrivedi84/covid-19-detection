let step = document.getElementsByClassName('step');
let prevBtn = document.getElementById('prev-btn');
let nextBtn = document.getElementById('next-btn');
let submitBtn = document.getElementById('submit-btn');
let form = document.getElementsByTagName('form')[0];
let preloader = document.getElementById('preloader-wrapper');
let bodyElement = document.querySelector('body');
let succcessDiv = document.getElementById('success');

form.onsubmit = () => {
    return false
}
let current_step = 0;
let stepCount = 5
step[current_step].classList.add('d-block');
if (current_step == 0) {
    prevBtn.classList.add('d-none');
    submitBtn.classList.add('d-none');
    nextBtn.classList.add('d-inline-block');
}

const progress = (value) => {
    document.getElementsByClassName('progress-bar')[0].style.width = `${value}%`;
}

nextBtn.addEventListener('click', () => {
    current_step++;
    let previous_step = current_step - 1;
    if ((current_step > 0) && (current_step <= stepCount)) {
        prevBtn.classList.remove('d-none');
        prevBtn.classList.add('d-inline-block');
        step[current_step].classList.remove('d-none');
        step[current_step].classList.add('d-block');
        step[previous_step].classList.remove('d-block');
        step[previous_step].classList.add('d-none');
        if (current_step == stepCount) {
            submitBtn.classList.remove('d-none');
            submitBtn.classList.add('d-inline-block');
            nextBtn.classList.remove('d-inline-block');
            nextBtn.classList.add('d-none');
        }
    } else {
        if (current_step > stepCount) {
            form.onsubmit = () => {
                return true
            }
        }
    }
    progress((100 / stepCount) * current_step);
});
 
 
prevBtn.addEventListener('click', () => {
    if (current_step > 0) {
        current_step--;
        let previous_step = current_step + 1;
        prevBtn.classList.add('d-none');
        prevBtn.classList.add('d-inline-block');
        step[current_step].classList.remove('d-none');
        step[current_step].classList.add('d-block')
        step[previous_step].classList.remove('d-block');
        step[previous_step].classList.add('d-none');
        if (current_step < stepCount) {
            submitBtn.classList.remove('d-inline-block');
            submitBtn.classList.add('d-none');
            nextBtn.classList.remove('d-none');
            nextBtn.classList.add('d-inline-block');
            prevBtn.classList.remove('d-none');
            prevBtn.classList.add('d-inline-block');
        }
    }
 
    if (current_step == 0) {
        prevBtn.classList.remove('d-inline-block');
        prevBtn.classList.add('d-none');
    }
    progress((100 / stepCount) * current_step);
});
 
 
submitBtn.addEventListener('click', async () => {
    preloader.classList.add('d-block');
 
    const timer = ms => new Promise(res => setTimeout(res, ms));
 
    await timer(3000)
        .then(() => {
            bodyElement.classList.add('loaded');
        }).then(() => {
            step[stepCount].classList.remove('d-block');
            step[stepCount].classList.add('d-none');
            prevBtn.classList.remove('d-inline-block');
            prevBtn.classList.add('d-none');
            submitBtn.classList.remove('d-inline-block');
            submitBtn.classList.add('d-none');
            succcessDiv.classList.remove('d-none');
            succcessDiv.classList.add('d-block');
        })
 
});

// Function to get the selected values from the form
function getSelectedValues() {
    let form = document.getElementsByTagName('form')[0];
    let formData = new FormData(form);

    // Convert the FormData object to a regular JavaScript object
    let data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    // Remove any unchecked checkboxes from the data object
    let checkboxes = form.querySelectorAll('input[type="checkbox"]');
    // checkboxes.forEach((checkbox) => {
    //     if (!checkbox.checked) {
    //         delete data[checkbox.name];
    //     }
    // });

    return data;
}

// Function to handle form submission
function handleSubmit() {
    let data = getSelectedValues();

    console.log('Data:', data);
    // Set up the Axios headers with the CSRF token
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': data.csrf_token
    };

    // Send the data using Axios
    axios.post('/submitform', data, { headers })
    .then(response => {
        // Handle the response from the Flask route if needed
        console.log('Response:', response.data);
    })
    .catch(error => {
        // Handle any errors
        console.error('Error:', error);
    });

    const timer = ms => new Promise(res => setTimeout(res, ms));
    timer(3000.5).then(() => window.location.href = '/dashboard')

}


// Attach the handleSubmit function to the submit button
document.getElementById('submit-btn').addEventListener('click', handleSubmit);

function handleNoneOfTheAboveChange() {
    const noneOfTheAboveCheckbox = document.getElementById('q_5_none');
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:not(#q_5_none)');

    if (noneOfTheAboveCheckbox.checked) {
        // If "None of the Above" checkbox is checked, deselect all other checkboxes
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    }
}

function handleOtherCheckboxChange(checkbox) {
    const noneOfTheAboveCheckbox = document.getElementById('q_5_none');

    if (checkbox.checked) {
        // If any other checkbox is checked, uncheck the "None of the Above" checkbox
        noneOfTheAboveCheckbox.checked = false;
    }
}
