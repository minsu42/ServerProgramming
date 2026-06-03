function toggleActive(element) {
    element.classList.toggle('active');
}

document.addEventListener("DOMContentLoaded", function() {
    // 카테고리 선택 상태를 토글하는 함수
    document.querySelectorAll('.category').forEach(item => {
        item.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    });
});

function submitForm() {
    // 비선호 카테고리 ID 배열 생성
    let nonPreferredCategories = [];
    document.querySelectorAll('.category.active').forEach(item => {
        nonPreferredCategories.push(item.id);
    });

    // FormData 객체 생성 및 로그인 정보와 비선호 카테고리 ID 배열 추가
    let formData = new FormData(document.getElementById('signupForm'));
    formData.append('nonPreferredCategories', JSON.stringify(nonPreferredCategories));

    // 서버로 FormData 전송 (예시 URL: '/signup', 실제 URL로 변경 필요)
    fetch('/signup', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.text();  // HTML 응답 처리
        }
    })
    .then(data => {
        if (data) {
            document.body.innerHTML = data;  // 새로운 HTML로 대체
        }
    })
    .catch(error => console.error('Error:', error));
}

