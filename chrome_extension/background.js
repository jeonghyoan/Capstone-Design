// 탭 업데이트 시 현재 탭 URL 정보 전송 요청
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('blog.naver.com')) {
        // URL 정보 저장 후 분류 요청
        var url = tab.url;

        // 분류 요청 처리
        fetch('http://127.0.0.1:5000/classify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ link: url }),
        })
            .then(response => response.json())
            .then(data => {
                // Send the result to the popup script
                chrome.runtime.sendMessage({ action: "sendResult", result: data.result });
            });
    }
});
