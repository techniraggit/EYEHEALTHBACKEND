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