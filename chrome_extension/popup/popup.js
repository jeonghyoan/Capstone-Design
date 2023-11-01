window.onload = function () {
    var resultText = document.getElementById("result");

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        var tab = tabs[0]; // 현재 활성화된 탭을 가져옵니다.
        fetch('http://127.0.0.1:5000/classify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ link: tab.url }),
        })
        .then(response => response.json())
        .then(data => {
            let result = data.result;
            if (result == -1) {
                resultText.textContent = '페이지를 볼 수 없음';
            } else if (result == 0) {
                resultText.textContent = '이 거친세상속 믿을만한리뷰ㅠ';
            } else if (result == 1) {
                resultText.textContent = '광곤데 믿었니?ㅋ';
            } else {
				resultText.textContent = '네이버 블로그인지 확인 부탁드립니다';
			}
        })
        .catch(console.error);
    });
};