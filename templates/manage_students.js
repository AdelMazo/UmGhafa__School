$(document).ready(function() {
    // Event listener for the Update buttons
    $(document).on('click', '.update-student-btn', function() {
        var studentId = $(this).data('student-id');
        
        // Fetch student data via AJAX
        $.ajax({
            url: '/update_student/' + studentId,
            method: 'GET',
            success: function(response) {
                // Load the Update Student form into the container
                $('#update_student_form_container').html(response);
            },
            error: function(xhr, status, error) {
                console.error(error);
            }
        });
    });

    // Event listener for the form submission
    $(document).on('submit', '#update_student_form', function(e) {
        e.preventDefault(); // Prevent default form submission
        
        // Serialize form data
        var formData = $(this).serialize();

        // Submit form data via AJAX
        $.ajax({
            url: $(this).attr('action'),
            method: $(this).attr('method'),
            data: formData,
            success: function(response) {
                // Hide the Update Student form after successful submission
                $('#update_student_form_container').html('');
                // Optionally, you can display a success message here or reload the student list
            },
            error: function(xhr, status, error) {
                console.error(error);
                // Optionally, you can display an error message here
            }
        });
    });
});
