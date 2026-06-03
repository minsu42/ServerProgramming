from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pymysql.cursors
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager(app)  # flask-login 확장

# 사용자 모델 class 정의
class User(UserMixin):
    def __init__(self, user_id, username, password, excluded_restaurants):
        self.id = user_id
        self.username = username
        self.password = password
        self.excluded_restaurants = excluded_restaurants



# MySQL에 저장
connection = pymysql.connect(
    host='ssu-server.cf60uusqyxge.ap-northeast-2.rds.amazonaws.com',
    user='root',
    password='rootroot',
    database='place_db',
    cursorclass=pymysql.cursors.DictCursor
)

# 질문 데이터 정의
questions = [
    {'id': 1, 'question': '어떤 시간대의 식사인가요?', 'options': ['아침', '점심', '저녁']},
    {'id': 2, 'question': '어느 정도 거리까지 갈 수 있나요?', 'options': ['바로 근처(100m)', '조금 더 가도 돼요(200m)', '멀리 가도 괜찮아요(500m)']}
]

category = ["barbecue_restaurant", "american_restaurant", "bakery", "brazilian_restaurant", "chinese_restaurant",
            "fast_food_restaurant", "italian_restaurant", "japanese_restaurant", "korean_restaurant",
            "pizza_restaurant", "sandwich_shop", "vietnamese_restaurant"]

def get_question_data(question_id):
    return next((q for q in questions if q['id'] == question_id), None)

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
    return None

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        user_id = request.form['id']
        password = request.form['password']
        excluded_restaurants = {category: request.form.get(f'excluded_{category}', 'False') == 'True' for category in category}

        with connection.cursor() as cursor:
            columns = ", ".join([f"excluded_{category}" for category in category])
            placeholders = ", ".join(["%s"] * (len(category) + 3))  # 여기를 +3으로 수정
            sql = f"INSERT INTO users (username, id, password, {columns}) VALUES ({placeholders})"
            values = [username, user_id, password] + [1 if excluded_restaurants[category] else 0 for category in category]
            cursor.execute(sql, values)
            connection.commit()
            flash('회원가입이 완료되었습니다. 로그인해 주세요.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', categories=category)

# 로그인 처리
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['id']
        password = request.form['password']
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




@app.route('/question/<int:question_id>')
def question(question_id):
    question_data = get_question_data(question_id)
    if question_data:
        previous_answers = {
            'question1_answer': session.get('question1_answer', ''),
            'question2_answer': session.get('question2_answer', ''),
            'question3_answer': session.get('question3_answer', '')
        }
        return render_template('question.html', question_id=question_id, question=question_data['question'],
                               options=question_data['options'], **previous_answers)
    else:
        return redirect(url_for('result'))

# 답변 처리
questions = [
    {'id': 1, 'question': '어떤 시간대의 식사인가요?', 'options': ['아침', '점심', '저녁']},
    {'id': 2, 'question': '어느 정도 거리까지 갈 수 있나요?', 'options': ['바로 근처(100m)', '조금 더 가도 돼요(200m)', '멀리 가도 괜찮아요(500m)']}
]

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



@app.route('/result/<question1_answer>/<question2_answer>')
def result(question1_answer, question2_answer):
    if current_user.is_authenticated:
        excluded_restaurants = current_user.excluded_restaurants
    else:
        excluded_restaurants = {}

    return render_template('result.html', excluded_restaurants=excluded_restaurants,
                           question1_answer=question1_answer, question2_answer=question2_answer)




# 로그아웃 처리
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user.name)

if __name__ == '__main__':
    app.run(debug=True)
