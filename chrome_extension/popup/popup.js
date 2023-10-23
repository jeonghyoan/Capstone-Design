window.onload = function () {
	var resultText = document.getElementById("result");

	chrome.runtime.sendMessage({action: "sendResult"}, function(response) {
		let result = response.result;
		if (result == -1) {
			resultText.textContent = '페이지를 볼 수 없음';
		} else if (result == 0) {
			resultText.textContent = '이 거친세상속 믿을만한리뷰ㅠ';
		} else if (result == 1) {
			resultText.textContent = '광곤데 믿었니?ㅋ';
		}
   });
};

