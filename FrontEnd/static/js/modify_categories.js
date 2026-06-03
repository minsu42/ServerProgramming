// 뒤로 가기 기능 추가
document.getElementById('back-button').onclick = function() {
    window.history.back();
};

function toggleActive(element) {
    element.classList.toggle('active');
}


// 카테고리 수정 정보
function submitForm() {
    // 비선호 카테고리 ID 배열 생성
    let nonPreferredCategories = [];
    document.querySelectorAll('.category.active').forEach(item => {
        nonPreferredCategories.push(item.id);
    });

    // FormData 객체 생성 및 비선호 카테고리 ID 배열 추가
    let formData = new FormData();
    formData.append('nonPreferredCategories', JSON.stringify(nonPreferredCategories));

    fetch('/modify', {
        method: 'PUT',
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


// 기존에 저장되어 있던 정보 반영
document.addEventListener('DOMContentLoaded', function() {
    fetch('/get_non_preferred_categories')
    .then(response => response.json())
    .then(data => {
        data.forEach(categoryId => {
            const categoryElement = document.getElementById(categoryId);
            if (categoryElement) {
                toggleActive(categoryElement);
            }
        });
    })
    .catch(error => console.error('Error:', error));
});
