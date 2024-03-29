import json

from requests import get
from data import db_session
from data.comments import Comments
from data.habits import Habits
from data.news import News
from data.users import User


def critical_id(content):
    db_session.global_init("../db/habits.db")
    db_sess = db_session.create_session()
    if content == 'user':
        return len(db_sess.query(User).all()) + 1
    elif content == 'news':
        return len(db_sess.query(News).all()) + 1
    elif content == 'habits':
        return len(db_sess.query(Habits).all()) + 1
    elif content == 'comments':
        return len(db_sess.query(Comments).all()) + 1


try:
    criticalid_user = critical_id('user')
    criticalid_news = critical_id('news')
    criticalid_habits = critical_id('habits')
    criticalid_comments = critical_id('comments')
    result = {}
    # Api users
    users_result = []
    users_result.append(
        {'content': 'UsersResource', 'request': "http://localhost:5000/api/v1/users/1",
         'response': get('http://localhost:5000/api/v1/users/1').json()})
    users_result.append(
        {'content': 'Wrong_UsersResource', 'request': "http://localhost:5000/api/v1/users/{}".format(criticalid_user),
         'response': get("http://localhost:5000/api/v1/users/{}".format(criticalid_user)).json()})
    users_result.append(
        {'content': 'UsersListResource', 'request': "http://localhost:5000/api/v1/users",
         'response': get('http://localhost:5000/api/v1/users').json()})
    result['users'] = users_result

    # Api news
    news_result = []
    news_result.append(
        {'content': 'NewsResource', 'request': "http://localhost:5000/api/v1/news/1",
         'response': get('http://localhost:5000/api/v1/news/1').json()})
    news_result.append(
        {'content': 'Wrong_NewsResource', 'request': "http://localhost:5000/api/v1/news/{}".format(criticalid_news),
         'response': get("http://localhost:5000/api/v1/news/{}".format(criticalid_news)).json()})
    news_result.append(
        {'content': 'NewsListResource', 'request': "http://localhost:5000/api/v1/news",
         'response': get('http://localhost:5000/api/v1/news').json()})
    result['news'] = news_result

    # Api habits
    habits_result = []
    habits_result.append(
        {'content': 'HabitsResource', 'request': "http://localhost:5000/api/v1/habits/1",
         'response': get('http://localhost:5000/api/v1/habits/1').json()})
    habits_result.append(
        {'content': 'Wrong_HabitsResource',
         'request': "http://localhost:5000/api/v1/habits/{}".format(criticalid_habits),
         'response': get("http://localhost:5000/api/v1/habits/{}".format(criticalid_habits)).json()})
    habits_result.append(
        {'content': 'HabitsListResource', 'request': "http://localhost:5000/api/v1/habits",
         'response': get('http://localhost:5000/api/v1/habits').json()})
    result['habit'] = habits_result

    # Api comments
    comments_result = []
    comments_result.append(
        {'content': 'CommentsResource', 'request': "http://localhost:5000/api/v1/comments/1",
         'response': get('http://localhost:5000/api/v1/comments/1').json()})
    comments_result.append(
        {'content': 'Wrong_CommentsResource',
         'request': "http://localhost:5000/api/v1/comments/{}".format(criticalid_comments),
         'response': get("http://localhost:5000/api/v1/comments/{}".format(criticalid_comments)).json()})
    comments_result.append(
        {'content': 'CommentsListResource', 'request': "http://localhost:5000/api/v1/comments",
         'response': get('http://localhost:5000/api/v1/comments').json()})
    result['comments'] = comments_result

    with open("resource_test_result.json", "w") as write_file:
        json.dump(result, write_file)
    print('Результаты записаны в resource_test_result.json.')
    print('Обратите внимание! Не забудьте кодировку utf-8 при открытии.')
except Exception:
    print(
        'Попробуйте провести тестирование со включенным main.py. ' +
        'Обратите внимание! Код идет на компьютере 127.0.0.1:5000, конец приложение app.run()')
    print('Обусловлено тем, что тесты должны быть локальными.')
