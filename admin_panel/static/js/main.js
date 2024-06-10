function showToaster(message, type) {
    var toaster = document.createElement('div');
    toaster.className = 'toaster ' + type;
    toaster.innerHTML = '<p class="message">' + message + '</p>';
    document.body.appendChild(toaster);
    setTimeout(function() {
        toaster.remove();
    }, 2000); // 2 seconds
}