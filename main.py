import datetime
import os
import random

from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api, abort
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

from data import db_session, user_resources, habit_resources, news_resources, comments_resources
from data.comments import Comments
from data.habits import Habits
from data.news import News
from data.users import User
from forms.AddHabit import AddHabitForm
from forms.AddNews import AddNewsForm
from forms.CommentForm import ComForm
from forms.Office import OfficeForm
from forms.RegisterForm import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
api.add_resource(user_resources.UsersResource, '/api/v1/users/<int:users_id>')
api.add_resource(user_resources.UsersListResource, '/api/v1/users')
api.add_resource(news_resources.NewsResource, '/api/v1/news/<int:news_id>')
api.add_resource(news_resources.NewsListResource, '/api/v1/news')
api.add_resource(habit_resources.HabitsResource, '/api/v1/habits/<int:habits_id>')
api.add_resource(habit_resources.HabitsListResource, '/api/v1/habits')
api.add_resource(comments_resources.CommentsResource, '/api/v1/comments/<int:comments_id>')
api.add_resource(comments_resources.CommentsListResource, '/api/v1/comments')
db_session.global_init("db/habits.db")
db_sess = db_session.create_session()
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """
    load_user - функция загрузки пользователя
    :param user_id: id user в базе данных
    :return: возвращается экземпляр класса User с нужным id
    """
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class LoginForm(FlaskForm):
    """
    Форма входа в существующий аккаунт
    """
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Обработка страницы /login - входа в существующий аккаунт
    :return: шаблон страницы с полями для ввода или ошибкой, в случае успешного ввода, user попадает на главную
    """
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, title='Авторизация')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    """
    Выход пользователя из аккаунта
    :return: выход на главную (без аккаунта)
    """
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    """
    Обработка главной страницы; формирование словарей(json: top_news, top_habits), которые определяют содержание главной страницы
    :return: шаблон главной страницы
    """
    db_sess = db_session.create_session()
    habits = db_sess.query(Habits).all()
    habits = sorted(habits, key=lambda x: -int(x.reposts))
    top_habits = []
    habit_index = 0
    for habit in habits:
        habit_index += 1
        creator_nickname = (db_sess.query(User).filter(User.id == habit.creator).first()).nickname
        top_habits.append({'id': habit.id,
                           'type': habit.type,
                           'period': habit.period,
                           'about_link': habit.about_link,
                           'count': habit.count,
                           'reposts': habit.reposts,
                           'creator': creator_nickname})
        if habit_index == 3:
            break
    rec_news = db_sess.query(News).all()
    rec_news = sorted(rec_news, key=lambda x: x.created_date)
    top_news = []
    news_index = 0
    for news in rec_news:
        path = ''
        news_index += 1
        creator_nickname = (db_sess.query(User).filter(User.id == news.user_id).first()).nickname
        for images in os.listdir('static/img/users_photo'):
            if images.split('.')[0] == creator_nickname:
                path = 'static/img/users_photo/' + images
        if path == '':
            path = 'static/img/users_photo/default.jpg'
        comments = []
        if news.comms:
            if ';' in news.comms:
                for com_id in news.comms.split(';'):
                    comments.append(db_sess.query(Comments).filter(Comments.id == com_id).first())
            elif len(news.comms) == 1:
                com_id = news.comms
                comments = [db_sess.query(Comments).filter(Comments.id == com_id).first()]
        else:
            comments = []
        if len(comments) > 1:
            comments = sorted(comments, key=lambda x: x.created_date)
        comments_main = []
        for com in comments:
            comentor_nickname = db_sess.query(User).filter(User.id == com.user_id).first().nickname
            comments_main.append({'id': com.id,
                                  'content': com.content,
                                  'created_date': com.created_date.strftime("%A %d %B %Y"),
                                  'creator': comentor_nickname})
        comments = comments_main
        top_news.append({'id': news.id,
                         'title': news.title,
                         'content': news.content,
                         'created_date': news.created_date.strftime("%A %d %B %Y"),
                         'comms': comments,
                         'creator': creator_nickname,
                         'path': path})
        if news_index == 3:
            break
    return render_template("index.html", top_habits=top_habits, top_news=top_news, random_id=random.randint(1, 2 ** 16),
                           title='Главная')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    """
    Обработка регистрации
    :return: форма регистрации
    """
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            nickname=form.nickname.data,
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/info', methods=['GET', 'POST'])
def about_page():
    """
    Обработка информационной страницы
    :return: шаблон страницы
    """
    return render_template('about.html', title='Информация')


@app.route("/add_habit", methods=['GET', 'POST'])
def add_habit():
    """
    Добавление привычки
    :return: шаблон для добавления
    """
    form = AddHabitForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        hab_id = len(db_sess.query(Habits).all()) + 1
        habit = Habits()
        habit.creator = current_user.id
        habit.count = 0
        habit.reposts = 0
        habit.type = form.habit_name.data
        habit.period = form.duration.data
        habit.about_link = form.about_habit.data
        db_sess.add(habit)
        db_sess.commit()
        if current_user.habit:
            current_user.habit += ';{}'.format(hab_id)
        else:
            current_user.habit = hab_id
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/office')
    return render_template("add_habit.html", form=form, title='Добавление привычки')


@app.route("/add_habit/<int:habit_id>", methods=['GET', 'POST'])
def repost_habit(habit_id):
    """
    Обработка репоста к себе привычки
    :param habit_id: id привычки в DB
    :return: главная страница(обновленная DB)
    """
    habit_id = habit_id
    db_sess = db_session.create_session()
    to_new = db_sess.query(User).filter(User.id == current_user.id).first()
    if to_new.habit and str(habit_id) not in str(to_new.habit):
        to_new.habit = str(to_new.habit) + ';' + str(habit_id)
    if not to_new.habit:
        to_new.habit = str(habit_id)
    db_sess.add(to_new)

    to_new2 = db_sess.query(Habits).filter(Habits.id == habit_id).first()
    to_new2.reposts = str(int(to_new2.reposts) + 1)
    db_sess.add(to_new2)
    db_sess.commit()
    return redirect('/')


@app.route("/com_add/<int:new_id>", methods=['GET', 'POST'])
def comm_add(new_id):
    """
    Обработка добавления комментария
    :param new_id: id новости в DB, к которой добавляется комментарий
    :return: форма для добавления комментария
    """
    form = ComForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        to_new = db_sess.query(News).filter(News.id == new_id).first()
        idd = len(db_sess.query(Comments).all()) + 1
        if len(to_new.comms) > 0:
            to_new.comms = str(to_new.comms) + ';{}'.format(idd)
        else:
            to_new.comms = idd
        com = Comments()
        com.user_id = current_user.id
        com.content = form.content.data
        com.created_date = datetime.datetime.now()
        db_sess.add(com)
        db_sess.add(to_new)
        db_sess.commit()
        return redirect('/')
    return render_template("add_com.html", form=form, title='Добавить комментарий')


@app.route("/office", methods=['GET', 'POST'])
@login_required
def my_office():
    """
    Обработка страницы профиля
    :return: страничка user
    """
    pathu = ''
    form = OfficeForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            form.name.data = user.name
            form.surname.data = user.surname
            form.nickname.data = user.nickname
            form.age.data = user.age
            form.status.data = user.status
            form.email.data = user.email
            form.city_from.data = user.city_from
        else:
            abort(404)
    if form.validate_on_submit():
        if '.jpg' in str(request.files['file']) or '.png' in str(request.files['file']):
            input_file = request.files['file']
            new_img = open("static/img/users_photo/" + str(current_user.nickname) + ".jpg", 'wb')
            new_img.write(input_file.read())
            new_img.close()
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            user.name = form.name.data
            user.surname = form.surname.data
            user.age = form.age.data
            user.status = form.status.data
            user.email = form.email.data
            user.city_from = form.city_from.data
            db_sess.commit()
            return redirect('/office')
        else:
            abort(404)
    for images in os.listdir('static/img/users_photo'):
        if images.split('.')[0] == current_user.nickname:
            pathu = 'static/img/users_photo/' + images
    if pathu == '':
        pathu = 'static/img/users_photo/default.jpg'
    db_sess = db_session.create_session()
    habits = []
    if current_user.habit:
        for el in current_user.habit.split(';'):
            habits.append(db_sess.query(Habits).filter(Habits.id == el).first())
    user_habits = []
    for habit in habits:
        user_habits.append({
            'id': habit.id,
            'type': habit.type,
            'period': habit.period,
            'about_link': habit.about_link,
            'count': habit.count,
            'reposts': habit.reposts,
            'creator': db_sess.query(User).filter(User.id == habit.creator).first().nickname,
        })
    unews = db_sess.query(News).filter(News.user_id == current_user.id).all()
    users_news = []
    for news in unews:
        path = ''
        creator_nickname = (db_sess.query(User).filter(User.id == news.user_id).first()).nickname
        for images in os.listdir('static/img/users_photo'):
            if images.split('.')[0] == creator_nickname:
                path = 'static/img/users_photo/' + images
        if path == '':
            path = 'static/img/users_photo/default.jpg'
        comments = []
        if news.comms:
            if ';' in news.comms:
                for com_id in news.comms.split(';'):
                    comments.append(db_sess.query(Comments).filter(Comments.id == com_id).first())
            elif len(news.comms) == 1:
                com_id = news.comms
                comments = [db_sess.query(Comments).filter(Comments.id == com_id).first()]
        else:
            comments = []
        if len(comments) > 1:
            comments = sorted(comments, key=lambda x: x.created_date)
        comments_main = []
        for com in comments:
            comentor_nickname = db_sess.query(User).filter(User.id == com.user_id).first().nickname
            comments_main.append({'id': com.id,
                                  'content': com.content,
                                  'created_date': com.created_date.strftime("%A %d %B %Y"),
                                  'creator': comentor_nickname})
        comments = comments_main
        users_news.append({'id': news.id,
                           'title': news.title,
                           'content': news.content,
                           'created_date': news.created_date.strftime("%A %d %B %Y"),
                           'comms': comments,
                           'creator': creator_nickname,
                           'path': path})
    return render_template('office.html',
                           form=form, path=pathu, random_id=random.randint(1, 2 ** 16), user_habits=user_habits,
                           users_news=users_news, title='Профиль')


@app.route("/add_news", methods=['GET', 'POST'])
def add_news():
    """
    Обработка добавления новости
    :return: шаблон для добавления
    """
    form = AddNewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.user_id = current_user.id
        news.title = form.news_name.data
        news.content = form.news_content.data
        db_sess.add(news)
        db_sess.commit()
        return redirect('/office')
    return render_template("add_news.html", form=form, title='Добавить новость')


@app.route("/news", methods=['GET', 'POST'])
def news():
    """
    Страница ленты
    :return: лента новостей
    """
    db_sess = db_session.create_session()
    rec_news = db_sess.query(News).all()
    top_news = []
    news_index = 0
    path = 'static/img/users_photo/default.jpg'
    for news in rec_news:
        path = ''
        news_index += 1
        creator_nickname = (db_sess.query(User).filter(User.id == news.user_id).first()).nickname
        for images in os.listdir('static/img/users_photo'):
            if images.split('.')[0] == creator_nickname:
                path = 'static/img/users_photo/' + images
        if path == '':
            path = 'static/img/users_photo/default.jpg'
        comments = []
        if news.comms:
            if ';' in news.comms:
                for com_id in news.comms.split(';'):
                    comments.append(db_sess.query(Comments).filter(Comments.id == com_id).first())
            elif len(news.comms) == 1:
                com_id = news.comms
                comments = [db_sess.query(Comments).filter(Comments.id == com_id).first()]
        else:
            comments = []
        if len(comments) > 1:
            comments = sorted(comments, key=lambda x: x.created_date)
        comments_main = []
        for com in comments:
            comentor_nickname = db_sess.query(User).filter(User.id == com.user_id).first().nickname
            comments_main.append({'id': com.id,
                                  'content': com.content,
                                  'created_date': com.created_date.strftime("%A %d %B %Y"),
                                  'creator': comentor_nickname})
        comments = comments_main
        top_news.append({'id': news.id,
                         'title': news.title,
                         'content': news.content,
                         'created_date': news.created_date.strftime("%A %d %B %Y"),
                         'comms': comments,
                         'creator': creator_nickname,
                         'path': path})
    return render_template("news.html", top_news=top_news, path=path, random_id=random.randint(1, 2 ** 16),
                           title='Лента')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run() для тестирования
