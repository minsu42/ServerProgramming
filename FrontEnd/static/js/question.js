function submitAnswer(questionId, answer) {
    fetch('/answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question_id: questionId, answer: answer }),
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = data.redirect; // 리디렉션
        updateProgress(); // 서버로부터 응답을 받고 나서 진행률 업데이트
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


let progress = 0; // 진행 상태를 나타내는 변수

function updateProgress() {

    // 현재 진행 상황을 가져옴
    let progress = parseInt(localStorage.getItem('progress') || '0');    

    if (progress < 50){
        progress += 50;
    }
    else{
        progress = 100;
    }

    // 업데이트된 진행 상황을 저장
    localStorage.setItem('progress', progress.toString());

    document.querySelector('.progress-text').textContent = `${progress}%`;
    document.querySelector('.progress-bar-fill').style.width = `${progress}%`;

    // 여기서 진행률이 100%에 도달했는지 확인하고, 도달했다면 진행 상태를 0으로 초기화
    if (progress === 100) {
        // 다음 질문 또는 세션을 위해 진행 상태를 0으로 초기화
        localStorage.setItem('progress', '0');
    }
}

// 페이지 로드 시 진행 상황 복원
document.addEventListener('DOMContentLoaded', (event) => {

    let progress = parseInt(localStorage.getItem('progress') || '0'); // 또는 sessionStorage 사용
    
    document.querySelector('.progress-text').textContent = `${progress}%`;
    document.querySelector('.progress-bar-fill').style.width = `${progress}%`;
});
