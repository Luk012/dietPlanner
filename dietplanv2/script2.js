document.getElementById('image-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('image-upload');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload an image first.");
        return;
    }

    const reader = new FileReader();
    reader.onloadend = function() {
        const base64String = reader.result.split(',')[1]; 
        
        const data = { image: base64String };

        fetch('/describe_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            const descriptionContainer = document.getElementById('description');
            descriptionContainer.innerHTML = `<p>${data.description}</p>`;
        })
        .catch(error => {
            console.error('Error:', error);
            const descriptionContainer = document.getElementById('description');
            descriptionContainer.innerHTML = '<p>There was an error processing your request. Please try again later.</p>';
        });
    };

    reader.readAsDataURL(file); 
});
