document.addEventListener('DOMContentLoaded', function() {
    function toggleContentFields() {
        const contentType = document.querySelector('#id_content_type').value;
        document.querySelector('.field-content_pdf').style.display = contentType === 'pdf' ? 'block' : 'none';
        document.querySelector('.field-content_text').style.display = contentType === 'direct' ? 'block' : 'none';
        document.querySelector('#taskcontentimage_set-group').style.display = contentType === 'direct' ? 'block' : 'none';
    }

    document.querySelector('#id_content_type').addEventListener('change', toggleContentFields);
    toggleContentFields();
});