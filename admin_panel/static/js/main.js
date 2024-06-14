function showToaster(message, type) {
    var toaster = document.createElement('div');
    toaster.className = 'toaster ' + type;
    toaster.innerHTML = '<p class="message">' + message + '</p>';
    document.body.appendChild(toaster);
    setTimeout(function() {
        toaster.remove();
    }, 2000); // 2 seconds
}


// this is ckeditor code for the future use and reference
// CKEDITOR.replace('description', {
//     toolbar: [
//         { name: 'paragraph', items: ['BulletedList'] },
        //{ name: 'basicstyles', items: ['Bold', 'Italic'] },
        //{ name: 'paragraph', items: ['NumberedList', 'BulletedList'] },
        //{ name: 'links', items: ['Link', 'Unlink'] },
        //{ name: 'insert', items: ['Image', 'Table'] },
        //{ name: 'styles', items: ['Format', 'Font', 'FontSize'] },
        //{ name: 'colors', items: ['TextColor', 'BGColor'] }
//     ]
// });