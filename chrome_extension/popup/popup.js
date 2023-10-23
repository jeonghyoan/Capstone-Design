window.onload = function () {

	var resultText = document.getElementById("result");

	chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
		if (request.action === "sendResult") {
			if (request.result == -1) {
				resultText.textContent = '페이지를 볼 수 없음';
			} else if (request.result == 0) {
				resultText.textContent = '이 거친세상속 믿을만한리뷰ㅠ';
			} else if (request.result == 1) {
				resultText.textContent = '광곤데 믿었니?ㅋ';
			}
		}

	});
};
