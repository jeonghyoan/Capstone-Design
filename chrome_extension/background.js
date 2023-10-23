chrome.runtime.onInstalled.addListener(() => {
    chrome.action.setBadgeBackgroundColor({ color: '#4688F1' });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.active && tab.url && (tab.url.startsWith('http://') || tab.url.startsWith('https://'))) {
        chrome.scripting.executeScript({
            target: { tabId },
            files: ['content.js'],
        });
    }
});

chrome.runtime.onMessage.addListener((request, sender) => {
    if (request.message === 'classificationResult') {
        // Display the result as a badge on the extension icon
        chrome.action.setBadgeText({ text: String(request.result) });
    }
});


