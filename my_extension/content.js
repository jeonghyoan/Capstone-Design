if (window.location.host === 'blog.naver.com') {
    let blogContent = document.querySelector('.se-main-container');
    if (blogContent) {
        let textContent = blogContent.innerText;
        console.log(textContent);
        // 여기서 textContent 전처리&모델에 입력해서 결과 받아야함
        // 히힛
    } else {
        console.log('No blog content found');
    }
}
