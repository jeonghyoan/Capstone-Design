let result = null;

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.action == "sendResult")
            sendResponse({result: result});
    }
);
