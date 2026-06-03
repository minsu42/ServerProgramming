import threading

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pymysql.cursors
import sys, os, json
from flask import g

from FrontEnd.GoogleAPI.restaurant_db import update_restaurant_data
from GoogleAPI.practice_kb import rst_from_question


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager(app)  # flask-login 확장

# 사용자 모델 class 정의
class User(UserMixin):
    def __init__(self, user_id, username, password, excluded_restaurants):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.excluded_restaurants = excluded_restaurants
        
    def get_id(self):
           return (self.user_id)

    def get_username(self):
        return self.username


# MySQL에 저장
connection = pymysql.connect(
    host='place-mysql.cf60uusqyxge.ap-northeast-2.rds.amazonaws.com',
    user='root',
    password='rootroot',
    database='place_db',
    cursorclass=pymysql.cursors.DictCursor
)


# 답변 처리
questions = [
    {'id': 1, 'question': '어떤 시간대의 식사인가요?', 'options': ['아침', '점심', '저녁']},
    {'id': 2, 'question': '어느 정도 거리까지 갈 수 있나요?', 'options': ['바로 근처(100m)', '조금 더 가도 돼요(200m)', '멀리 가도 괜찮아요(500m)']}
]

def get_question_data(question_id):
    return next((q for q in questions if q['id'] == question_id), None)

category = ["barbecue_restaurant", "american_restaurant", "bakery", "brazilian_restaurant", "chinese_restaurant",
            "fast_food_restaurant", "italian_restaurant", "japanese_restaurant", "korean_restaurant",
            "pizza_restaurant", "sandwich_shop", "vietnamese_restaurant"]


# Flask-Login에서 사용자 객체를 로드
@login_manager.user_loader
def load_user(user_id):
    with connection.cursor() as cursor:
        sql = "SELECT * FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            excluded_restaurants = {category: user_data[f'excluded_{category}'] for category in category}
            return User(user_data['id'], user_data['username'], user_data['password'], excluded_restaurants)

# 시작 화면
@app.route('/')
def start():
    # 백그라운드 스레드에서 데이터베이스 업데이트 시작
    threading.Thread(target=update_restaurant_data).start()
    return render_template('start.html')  # 계정 페이지 렌더링


# 로그인 처리
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user-id']
        password = request.form['user-password']
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id = %s AND password = %s"
            cursor.execute(sql, (user_id, password))
            user_data = cursor.fetchone()
            if user_data:
                excluded_restaurants = {category: user_data[f'excluded_{category}'] for category in category}
                user = User(user_data['id'], user_data['username'], user_data['password'], excluded_restaurants)
                login_user(user)
                return redirect(url_for('question', question_id=1))
            else:
                flash('로그인 실패: 아이디 또는 비밀번호가 잘못되었습니다.', 'error')
    return render_template('login.html')

# 회원가입
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['user-username']
        user_id = request.form['user-id']
        password = request.form['user-password']
        # 비선호 카테고리 JSON 문자열을 파싱하여 리스트로 변환
        non_preferred_categories = json.loads(request.form['nonPreferredCategories'])
        excluded_restaurants = {category: (category in non_preferred_categories) for category in category}
        with connection.cursor() as cursor:
            columns = ", ".join([f"excluded_{category}" for category in category])
            placeholders = ", ".join(["%s"] * (len(category) + 3))  # 여기를 +3으로 수정
            sql = f"INSERT INTO users (username, id, password, {columns}) VALUES ({placeholders})"
            values = [username, user_id, password] + [1 if excluded_restaurants[category] else 0 for category in category]
            cursor.execute(sql, values)
            connection.commit()
            # flash('회원가입이 완료되었습니다. 로그인해 주세요.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html', categories=category)


# 답변 처리
@app.route('/answer', methods=['POST'])
def answer():
    data = request.get_json()
    question_id = int(data['question_id'])
    answer = data['answer']

    session['question' + str(question_id) + '_answer'] = answer

    if question_id == 2:  # 마지막 질문일 경우, 결과 페이지로 리다이렉트
        with connection.cursor() as cursor:
            sql = "INSERT INTO users_responses (username, question1_answer, question2_answer) VALUES (%s, %s, %s)"
            values = (current_user.username if current_user.is_authenticated else 'guest', session['question1_answer'], session['question2_answer'])
            cursor.execute(sql, values)
            connection.commit()
        return jsonify({'redirect': url_for('result', question1_answer=session['question1_answer'], question2_answer=session['question2_answer'])})
    else:
        next_question_id = question_id + 1
        return jsonify({'redirect': url_for('question', question_id=next_question_id)})


@app.route('/question/<int:question_id>')
def question(question_id):
    question_data = get_question_data(question_id)
    if question_data:
        previous_answers = {
            'question1_answer': session.get('question1_answer', ''),
            'question2_answer': session.get('question2_answer', ''),
        }
        return render_template('question.html', question_id=question_id, question=question_data['question'],
                               options=question_data['options'], **previous_answers)
    else:
        return redirect(url_for('result'))


# 내 정보
@app.route('/myaccount')
@login_required
def myaccount():
    return render_template('myaccount.html', is_authenticated=current_user.is_authenticated)  # 계정 페이지 렌더링

# 카테고리 수정
@app.route('/modify_categories')
def modify_categories():
    return render_template('modify_categories.html')  # 계정 페이지 렌더링


# 전에 저장한 카테고리 가져오는 함수
@app.route('/get_non_preferred_categories')
def get_non_preferred_categories():
    user_id = current_user.user_id
    columns = [f"excluded_{category}" for category in category]

    query = f"""
        SELECT {', '.join(columns)}
        FROM `users`
        WHERE `id` = %s
    """

    # try:
    with connection.cursor() as cursor:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        
        # 비선호 카테고리만 필터링
        non_preferred_categories = [
            col.replace('excluded_', '') for col, val in result.items() if val == 1
        ]
            

    return jsonify(non_preferred_categories)

# 카테고리 업데이트 하는 함수
@app.route('/modify', methods=['PUT'])
@login_required
def modify():
    user_id = current_user.user_id
    non_preferred_categories = json.loads(request.form['nonPreferredCategories'])

    excluded_restaurants = {category: (category in non_preferred_categories) for category in category}

    # try:
    with connection.cursor() as cursor:
        columns = ", ".join([f"excluded_{category} = %s" for category in category])
        sql = f"UPDATE users SET {columns} WHERE id = %s"
        values = [1 if excluded_restaurants[category] else 0 for category in category] + [user_id]
        cursor.execute(sql, values)
        connection.commit()

    return redirect(url_for('myaccount'))

        

# 로그아웃 처리
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('start'))


# 계정 삭제
@app.route('/delete_account', methods=['DELETE'])
@login_required
def delete_account():
    user_id = current_user.user_id
    with connection.cursor() as cursor:
        # 사용자 ID에 해당하는 레코드를 삭제
        sql = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        connection.commit()
    logout_user()  # 로그아웃 처리
    return jsonify(success=True)
            


@app.route('/result/<question1_answer>/<question2_answer>')
def result(question1_answer, question2_answer):
    is_authenticated = current_user.is_authenticated
    if current_user.is_authenticated:
        excluded_restaurants = current_user.excluded_restaurants
        print(excluded_restaurants)
        place_result = rst_from_question(current_user.username, excluded_restaurants)
        print(current_user.username)
    else:
        excluded_restaurants = {'barbecue_restaurant': 0, 'american_restaurant': 0, 'bakery': 0, 'brazilian_restaurant': 0, 'chinese_restaurant': 0, 'fast_food_restaurant': 0, 'italian_restaurant': 0, 'japanese_restaurant': 0, 'korean_restaurant': 0, 'pizza_restaurant': 0, 'sandwich_shop': 0, 'vietnamese_restaurant': 0}
        place_result = rst_from_question("guest", excluded_restaurants)

    if place_result == -1 or len(place_result) == 0:
        flash('조건에 일치하는 식당이 없습니다', 'warning')  # 사용자에게 경고 메시지를 표시
        return redirect(url_for('question', question_id=1))

    return render_template('result.html', is_authenticated=is_authenticated,
                           excluded_restaurants=excluded_restaurants,
                           question1_answer=question1_answer, question2_answer=question2_answer,
                           place_result=place_result)

if __name__ == '__main__':
    app.run(debug=True)  # 디버그 모드로 애플리케이션 실행
