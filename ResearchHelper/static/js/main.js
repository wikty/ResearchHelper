$(function() {
      'use strict';

      // Custome form validation
      window.addEventListener('load', function() {
        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.getElementsByClassName('needs-validation');
        // Loop over them and prevent submission
        var validation = Array.prototype.filter.call(forms, function(form) {
          form.addEventListener('submit', function(event) {
            if (form.checkValidity() === false) {
              event.preventDefault();
              event.stopPropagation();
            }
            form.classList.add('was-validated');
          }, false);
        });
      }, false);

      // enable tooltip
      $('[data-toggle="tooltip"]').tooltip();
    // var progressBarModal = $('#progress-bar-modal');
    // var progressBar = $('#progress-bar');

    // $('.form-upload').ajaxForm({
    //     beforeSend: function() {
    //         progressBarModal.modal('show');
    //         progressBar.width('0%');
    //         progressBar.html('0%');
    //     },
    //     uploadProgress: function(event, position, total, percentComplete) {
    //         var percentVal = percentComplete + '%';
    //         progressBar.width(percentVal);
    //         progressBar.html(percentVal);
    //     },
    //     success: function() {
    //         progressBar.width('100%');
    //         progressBar.html('100%');
    //         progressBarModal.modal('hide');
    //     },
    //     complete: function(xhr) {
    //         console.log(xhr);
    //         // document.write(xhr.responseText);
    //     }
    // });
}); 