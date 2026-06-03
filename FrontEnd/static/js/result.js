var mySwiper = new Swiper ('.swiper-container', {
    // Optional parameters
    direction: 'horizontal',
    slidersPerView: 'auto',
    centeredSlides: true,
    on: {
        slideChange: function () {
            updateTop(this.activeIndex + 1); // 슬라이드가 변경될 때마다 호출
        }
    }
});

// top 요소를 업데이트하는 함수
function updateTop(index) {
    var topElement = document.getElementById('top');
    topElement.innerText = 'Top' + index; // 'TopN' 형태로 텍스트 변경
}

// 초기 슬라이드에 대한 top 요소 업데이트
updateTop(1); // 페이지 로드 시 첫 번째 슬라이드에 대해 실행

function checkLogin(isAuthenticated) {
    if (!isAuthenticated) {
        if (confirm('로그인해야 이용할 수 있습니다. 로그인 페이지로 이동하시겠습니까?')) {
            window.location.href = "/login";
        }
    } else {
        window.location.href = "/myaccount";
    }
}