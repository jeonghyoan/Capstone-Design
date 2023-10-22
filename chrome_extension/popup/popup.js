document.addEventListener('DOMContentLoaded', () => {
    chrome.action.getBadgeText({}, (result) => {
        let message = "";
        if (result === "1") {
            message = "This is an advertisement.";
        } else if (result === "0") {
            message = "This is a trustworthy review.";
        }
        
        // Display the result in the popup.
        // This depends on how you have set up your popup.html.
        
        let resultElement = document.getElementById('result');  // Assuming there's an element with id 'result' in your popup.html
        if (resultElement) {
            resultElement.textContent = message;
        }
    });
});

