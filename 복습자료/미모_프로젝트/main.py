from flask import Flask   # Flask 도구 가져오기

app = Flask(__name__)     # Flask 앱(식당) 만들기

@app.route('/')           # '/' 주소에 손님이 들어오면
def home():               # 주방장이 이 함수를 실행
    return "안녕하세요! 여기는 Flask 식당이에요 🍽️"

app.run(debug=True)       # 식당 문 열기 (서버 실행)
