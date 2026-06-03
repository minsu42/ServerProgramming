function logout() {
    // 서버에 로그아웃 요청을 보냄
    window.location.href = "/logout"; // Flask의 logout 라우트로 리다이렉트
}

function deleteAccount() {
    if (confirm("정말로 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")) {
        fetch('/delete_account', {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("계정이 성공적으로 삭제되었습니다.");
                window.location.href = "/";  // 시작 화면으로 리디렉션합니다.
            } else {
                alert("계정 삭제에 실패했습니다. 다시 시도해 주세요.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("계정 삭제 중 오류가 발생했습니다.");
        });
    }
}