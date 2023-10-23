let result = null;

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && /^http/.test(tab.url)) {
        fetch('http://127.0.0.1:5000/classify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ link: tab.url }),
        })
        .then(response => response.json())
        .then(data => result = data.result)
        .catch(console.error);
    }
});

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.action == "sendResult")
            sendResponse({result: result});
    }
);
