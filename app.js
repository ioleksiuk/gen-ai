async function generateImage(description) {
    const response = await fetch('http://localhost:5000/generate-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({text: description})
    });
    if (response.ok) {
        const data = await response.json();
        console.log(data);
        // Handle success
    } else {
        console.error('Failed to generate image');
        // Handle error
    }
}

generateImage('Describe the scene you want to generate.');
