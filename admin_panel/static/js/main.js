function showToaster(message, type) {
    var toaster = document.createElement('div');
    toaster.className = 'toaster ' + type;
    toaster.innerHTML = '<p class="message">' + message + '</p>';
    document.body.appendChild(toaster);
    setTimeout(function () {
        toaster.remove();
    }, 3000); // 3 seconds
}

function credEncode(data) {
    let encodedData = data;
    for (let i = 0; i < 3; i++) {
        console.log(i)
        encodedData = btoa(encodedData);
    }
    return encodedData;
}

function credDecode(encoded_data) {
    let decodedData = encoded_data;
    for (let i = 0; i < 3; i++) {

        decodedData = atob(decodedData);
    }
    return decodedData;
}

function validatePhoneNumber(phoneNumber) {
    const phoneRegex = /^\+[1-9][0-9]{1,3}[0-9]{7,10}$/;
    return phoneRegex.test(phoneNumber);
}

function showError(selector, message) {
    $(selector).siblings('.error-message').remove();
    if (message) {
        $(selector).after(`<span class="error-message text-danger">${message}</span>`);
    }
}

function validateEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}