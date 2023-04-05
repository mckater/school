from flask import Flask, redirect, render_template, request, session
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
import random
import logging
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.login_form import MainClassTable

app = Flask(__name__)
app.config['SECRET_KEY'] = '~!@#$_secretkey'

UNITS = {0: 'бит', 3: 'байт', 13: 'Кбайт', 23: 'Мбайт', 33: 'Гбайт', 43: 'Тбайт'}


class Process:
    def __init__(self):
        self.name = ''
        self.score = 0
        self.done = False
        self.data = dict()

    def tasks_(self, current_user_id):
        tasks = list()
        flag = random.choice((True, False))
        for i in range(5):
            flag = not flag
            coeff = random.choice(random.sample(range(1, 20), 10))
            if flag:  # умножение
                power_from = random.choice(list(UNITS)[-4:])
                delta = random.choice((10, 20))
                while power_from - delta < 0:
                    delta = power_from
                power_to = power_from - delta
                from_unit = UNITS[power_from]
                answer = str(coeff * 2 ** delta)
                size = coeff
                to_unit = UNITS[power_to]
            else:  # деление
                power_from = random.choice(list(UNITS)[:4])
                delta = random.choice((10, 20))
                if not (power_from + delta) % 10:
                    delta += 3
                size = coeff * 2 ** delta
                power_to = power_from + delta
                from_unit = UNITS[power_from]
                answer = str(coeff)
                to_unit = UNITS[power_to]

            tasks.append({
                'id': i + 1,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'size': size,
                'answer': answer,
                'correct': False,
                'result': ''
            })
        self.data[current_user_id] = tasks
        return

    def tasks_cases(self, current_user_id):
        tasks = list()
        for i in range(5):
            k = random.choice((2, 3, 4, 5, 6, 7, 8))
            size = random.choice([x for x in range(10, 80, 10)]) * k
            one = random.randint(1, 8) * 128
            two = eval('%i %s %s' % (one, '*', k))
            li = [one, two]
            random.shuffle(li)
            answer = str(size * li[0] // li[1])
            tasks.append({
                'id': i + 1,
                'from_unit': li[0],
                'to_unit': li[1],
                'size': size,
                'answer': answer,
                'correct': False,
                'result': ''
            })
        self.data[current_user_id] = tasks
        return


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    db_sess = db_session.create_session()
    return db_sess.query(MainClassTable).get(id)


class MyclassForm(FlaskForm):
    id = StringField('id', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = MyclassForm()
    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(MainClassTable).filter(MainClassTable.id == form_login.id.data).first()
        if user and user.check_password(form_login.password.data):
            login_user(user, remember=form_login.remember_me.data)
            return redirect("/main")
        return render_template('login.html', message="Wrong login or password", form=form_login)
    return render_template('login.html', title='Авторизация', form=form_login)


@app.route("/")
# @app.route('/index')
def index():
    return redirect("/login")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


class TaskForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    answer = StringField('answer', validators=[DataRequired()])
    answer1 = StringField('answer1', validators=[DataRequired()])
    answer2 = StringField('answer2', validators=[DataRequired()])
    answer3 = StringField('answer3', validators=[DataRequired()])
    answer4 = StringField('answer4', validators=[DataRequired()])
    submit = SubmitField('Ответить')


@app.route('/main', methods=['GET', 'POST'])
def main():
    # print(current_user)
    form = TaskForm()
    ex.name = ''
    ex.score = 0
    ex.done = False
    if request.method == 'GET':  # обработка GET запроса
        ex.tasks_(current_user.id)
        if not session.get('task_results'):
            session['task_results'] = []
        return render_template('main.html', form=form, tasks=ex.data[current_user.id],
                               score=ex.score, done=ex.done)

    if request.method == 'POST' and form.validate_on_submit():
        task_results_ = session['task_results']
        try:
            answer_data = form.answer.data.strip().replace(' ', '')
            task_results_.append(answer_data)
            ex.data[current_user.id][0]['result'] = answer_data
            answer_data = form.answer1.data.strip().replace(' ', '')
            task_results_.append(answer_data)
            ex.data[current_user.id][1]['result'] = answer_data
            answer_data = form.answer2.data.strip().replace(' ', '')
            task_results_.append(answer_data)
            ex.data[current_user.id][2]['result'] = answer_data
            answer_data = form.answer3.data.strip().replace(' ', '')
            task_results_.append(answer_data)
            ex.data[current_user.id][3]['result'] = answer_data
            answer_data = form.answer4.data.strip().replace(' ', '')
            task_results_.append(answer_data)
            ex.data[current_user.id][4]['result'] = answer_data

            ex.name = form.name.data.strip()
            for task in ex.data[current_user.id]:
                if task['answer'] == task_results_[task['id'] - 1]:
                    task['correct'] = True
                    ex.score += 1
            ex.done = True
            return render_template('result.html', name=ex.name, tasks=ex.data[current_user.id], score=ex.score, done=ex.done)
            # session.clear()  # очистка списка выполненных заданий в сеансе
        except Exception:
            logging.exception('')
            return ''


@app.route('/cases', methods=['GET', 'POST'])
def cases():
    form = TaskForm()
    ex.name = ''
    ex.score = 0
    ex.done = False

    if request.method == 'GET':  # обработка GET запроса
        ex.tasks_cases(current_user.id)
        if not session.get('task_results'):
            session['task_results'] = []

        return render_template('cases.html', form=form, tasks=ex.data[current_user.id],
                               score=ex.score, done=ex.done)

    if request.method == 'POST' and form.validate_on_submit():
        task_results_ = session['task_results']
        try:
            answer_data = form.answer.data.strip().replace(' ', '')
            task_results_.append(answer_data)
            ex.data[current_user.id][0]['result'] = answer_data
            answer_data = form.answer1.data.strip().replace(' ', '')
            task_results_.append(answer_data)
            ex.data[current_user.id][1]['result'] = answer_data
            answer_data = form.answer2.data.strip().replace(' ', '')
            task_results_.append(answer_data)
            ex.data[current_user.id][2]['result'] = answer_data
            answer_data = form.answer3.data.strip().replace(' ', '')
            task_results_.append(answer_data)
            ex.data[current_user.id][3]['result'] = answer_data
            answer_data = form.answer4.data.strip().replace(' ', '')
            task_results_.append(answer_data)
            ex.data[current_user.id][4]['result'] = answer_data

            ex.name = form.name.data.strip()
            for task in ex.data[current_user.id]:
                if task['answer'] == task_results_[task['id'] - 1]:
                    task['correct'] = True
                    ex.score += 1
            ex.done = True
            return render_template('result_cases.html', name=ex.name, tasks=ex.data[current_user.id],
                                   score=ex.score, done=ex.done)
            # session.clear()  # очистка списка выполненных заданий в сеансе
        except Exception:
            logging.exception('')
            return ''


if __name__ == '__main__':
    db_session.global_init("db/class.db")
    ex = Process()
    app.run(debug=True)
