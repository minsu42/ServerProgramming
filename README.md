# 🍽️ 위치·취향 기반 식당 추천 웹 서비스

> 사용자의 **위치**와 **음식 취향**, **식사 상황(시간대·이동 거리)** 을 입력받아 맞춤 식당을 추천하는 웹 서비스
> 숭실대학교 「서버 프로그래밍」 팀 프로젝트 (4인)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Amazon RDS](https://img.shields.io/badge/Amazon%20RDS-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white)
![Google Maps](https://img.shields.io/badge/Google%20Places%20API-4285F4?style=for-the-badge&logo=googlemaps&logoColor=white)

<br>

## 📌 프로젝트 소개

"점심 뭐 먹지?"라는 일상적인 고민을 줄이기 위해 시작한 프로젝트입니다.
사용자가 **싫어하는 음식 카테고리**를 미리 설정해 두고, 식사할 때마다 **시간대와 이동 가능 거리**만 선택하면, 그 조건에 맞는 주변 식당을 추천받을 수 있습니다.

서버 측에서는 **사용자 취향 데이터를 관계형 DB로 관리**하고, **위치 기반 식당 데이터와 조합해 추천 결과를 만들어내는 비즈니스 로직**을 구현하는 데 집중했습니다.

<br>

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 🔐 회원/비회원 인증 | Flask-Login 기반 세션 인증, 비회원(게스트) 이용 지원 |
| 🍱 취향 설정 | 12개 음식 카테고리(한식·중식·일식·양식·분식 등) 중 **제외할 음식** 선택 |
| ❓ 상황 기반 질문 | 식사 시간대(아침·점심·저녁), 이동 가능 거리(100m·200m·500m) 입력 |
| 📍 맞춤 추천 | 사용자 취향·상황 + 위치 데이터를 조합해 식당 후보 필터링 및 추천 |
| 💾 응답 저장 | 사용자 질문 응답을 DB에 저장해 추천 근거로 활용 |

<br>

## 🛠️ 기술 스택

| 구분 | 기술 |
|------|------|
| **Backend** | Python, Flask, Flask-Login, WTForms |
| **Database** | MySQL (AWS RDS), PyMySQL |
| **Frontend** | HTML, CSS, JavaScript, Jinja2 |
| **External API** | Google Places API (위치 기반 식당 데이터) |
| **Tooling** | Git, PyCharm |

<br>

## 🗂️ ERD

도메인(회원 정보 · 질문 응답 · 음식 카테고리 · 식당 리스트)을 분리하고 관계를 정의해 설계했습니다.

![ERD](./서버%20프로그래밍%20ERD.png)

<br>

## 🗄️ 데이터베이스 설계

MySQL 인스턴스를 **AWS RDS**에 올려 팀원 모두가 공통으로 접근하도록 구성했습니다.

| 테이블 | 역할 |
|--------|------|
| `users` | 회원 기본 정보 및 음식 카테고리별 제외 여부 |
| `users_responses` | 사용자 질문 응답(시간대·거리 등) 기록 |
| 식당/카테고리 리스트 | 음식 카테고리별 식당 데이터 (한식·중식·일식·양식·분식 등) |

<br>

## 👥 팀 구성 및 담당 역할

**팀 구성:** 4인 (백엔드 · 프론트엔드 · 데이터 · 기획)

**주요 담당 (강민수)**
- 백엔드 API 및 **추천 비즈니스 로직** 구현
- **MySQL ERD 설계 및 DB 연동** (PyMySQL)
- Flask-Login 기반 **회원/비회원 인증 및 세션 관리**
- 회원가입 동적 쿼리 처리 및 사용자 취향 데이터 저장 로직

<br>

## 🧩 트러블슈팅 & 배운 점

**회원가입 동적 INSERT 쿼리 실패**

사용자별로 12개 음식 카테고리의 제외 여부를 저장하기 위해, 컬럼과 값을 동적으로 생성해 `INSERT`하는 방식을 사용했습니다. 그런데 회원가입이 계속 실패했고, 에러를 추적해 보니 **INSERT 문의 컬럼 개수와 `VALUES`의 플레이스홀더(`%s`) 개수가 일치하지 않는 것**이 원인이었습니다. 컬럼 문자열을 만들 때 카테고리 12개만 세고 기본 컬럼 3개(이름·아이디·비밀번호)를 빠뜨린 것이었습니다.

→ 플레이스홀더 개수를 `카테고리 수 + 기본 컬럼 3개`로 맞춰 해결하고, 이후 컬럼·값 목록을 같은 기준으로 생성하도록 정리해 재발을 막았습니다.

이 과정에서 **편의를 위한 단순화(카테고리를 컬럼으로 둔 설계)가 오히려 쿼리를 복잡하게 만들고 버그 위험을 키운다**는 점을 체감했고, 관계형 DB에 데이터를 넣을 때 **스키마와 쿼리의 정합성을 먼저 검증**하는 습관을 얻었습니다.

<br>

## 📁 프로젝트 구조

```
ServerProgramming/
├── Backend/                # Flask 서버, 라우팅, DB 연동, 비즈니스 로직
├── FrontEnd/               # 화면 (HTML/CSS/JS)
├── GoogleAPI/              # Google Places API 연동 (위치 기반 식당 데이터)
├── 회의록/                  # 팀 회의 기록
├── 서버 프로그래밍 ERD.png    # 데이터베이스 ERD
├── 서버 1팀.pptx            # 발표 자료
└── README.md
```

<br>

## ⚙️ 실행 방법

```bash
# 1. 의존성 설치
pip install flask flask-login pymysql flask-wtf

# 2. DB 접속 정보 설정
#    Backend의 DB 연결 설정(host, user, password, database)을 환경에 맞게 수정

# 3. 서버 실행
python Backend/app.py   # 실제 진입 파일명에 맞게 수정
```

> ⚠️ DB 접속 정보·시크릿 키 등 민감 정보는 환경변수로 분리하는 것을 권장합니다.
