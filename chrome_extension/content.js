window.addEventListener('load', () => {
    if (window.location.href.includes('blog.naver.com')) {
        let url = window.location.href;
        fetch('http://localhost:5000/classify', {  // Replace with your Flask server URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({url: url}),
        })
        .then(response => response.json())
        .then(data => {
            chrome.runtime.sendMessage({message: "classificationResult", result: data.result});
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
});


