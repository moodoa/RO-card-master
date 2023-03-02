from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import json
import time

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+pymysql://admin:password@endpoint/database"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'some_secret_key'

db = SQLAlchemy(app)

class Scoreboard(db.Model):
    __tablename__ = "Scoreboard"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Scoreboard {self.name}>"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/startgame", methods = ["POST", "GET"])
def start_game():
    with open("cards.json", "r", encoding="utf-8-sig") as file:
        data = json.load(file)
    session["questions"] = random.sample(list(data.values()), 80)
    session["score"] = 0
    session["question_cnt"] = 1
    session["name"] = request.form["your_name"]
    return redirect(url_for("gamepage"))

@app.route("/gamepage")
def gamepage():
    score = session["score"]
    question_cnt = session["question_cnt"]
    session["start_time"] = time.time()
    try:
        current_questions = session["questions"][:4]
        session["answer"] = current_questions[0]["title"]
        current_img = current_questions[0]["image"]
        current_name = current_questions[0]["name"]
        current_answers = [x["title"] for x in current_questions]
        random.shuffle(current_answers)
        session["questions"] = session["questions"][4:]
    except:
        return redirect(url_for("scoreboard"))
    return render_template('game.html', current_img = current_img, current_name = current_name, current_answers=current_answers, score = score, question_cnt = question_cnt)

@app.route("/answer_check", methods=["POST"])
def answer_check():
    used_time = time.time()-session["start_time"]
    player_ans = request.form["player_ans"]
    if player_ans == session["answer"]:
        session["score"] += max(12-int(used_time), 0)
    session["question_cnt"] += 1
    return redirect(url_for("gamepage"))

@app.route("/scoreboard")
def scoreboard():
    score = session["score"]
    name = str(session["name"])
    new_info = Scoreboard(
        name=name, score=score
    )
    try:
        db.session.add(new_info)
        db.session.commit()
    except:
        pass
    infos = Scoreboard.query.order_by(Scoreboard.score.desc()).limit(5)
    return render_template("scoreboard.html", infos = infos, score = score, name = name)


if __name__ == "__main__":
    app.run()