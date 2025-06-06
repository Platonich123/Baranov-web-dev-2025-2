import random
from functools import lru_cache
from flask import Flask, render_template, abort
from faker import Faker
import os

fake = Faker()

app = Flask(__name__, 
           template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')),
           static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'static')))
#application = app

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7']

def generate_comments(replies=True):
    comments = []
    for _ in range(random.randint(1, 3)):
        comment = {
            'author': fake.name(),
            'text': fake.paragraph(nb_sentences=2),  # Более короткие комментарии
            'date': fake.date_time_between(start_date='-1y', end_date='now')  # Добавляем дату комментария
        }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    posts_content = [
        {
            'title': 'Как начать карьеру в IT',
            'text': '''В современном мире IT-индустрия предлагает множество возможностей для построения успешной карьеры. 
            Независимо от вашего текущего опыта и образования, существует несколько проверенных путей для входа в эту сферу.

            Первый шаг - определиться с направлением. Front-end разработка, back-end, мобильная разработка, data science или 
            тестирование - каждая область имеет свои особенности и требования. Важно выбрать то, что действительно вам интересно.

            Второй важный момент - это обучение. Сегодня доступно множество онлайн-курсов, bootcamp-программ и учебных материалов. 
            Ключевое здесь - практика. Создавайте свои проекты, участвуйте в open-source разработке, решайте задачи на 
            платформах вроде LeetCode или HackerRank.

            Не менее важно развивать soft skills. Умение работать в команде, коммуникабельность, способность к самообучению - 
            эти навыки часто ценятся не меньше технических знаний.''',
            'author': 'Елена Волкова',
            'date': fake.date_time_between(start_date='-2y', end_date='now'),
            'image_id': images_ids[0] + '.jpg'
        },
        {
            'title': 'Искусственный интеллект в повседневной жизни',
            'text': '''Искусственный интеллект уже давно перестал быть чем-то из области научной фантастики. Сегодня мы 
            взаимодействуем с ИИ практически каждый день, часто даже не замечая этого.

            Голосовые помощники в наших смартфонах, рекомендательные системы в онлайн-магазинах и стриминговых сервисах, 
            автоматические переводчики и системы распознавания лиц - всё это примеры использования ИИ в повседневной жизни.

            Особенно интересно наблюдать за развитием генеративного ИИ. Такие инструменты как ChatGPT и Midjourney 
            демонстрируют впечатляющие способности в создании текстов, изображений и даже музыки. Это открывает новые 
            возможности для творчества и решения повседневных задач.

            При этом важно помнить о этических аспектах использования ИИ и сохранять критическое мышление при работе с 
            такими системами.''',
            'author': 'Михаил Соколов',
            'date': fake.date_time_between(start_date='-2y', end_date='now'),
            'image_id': images_ids[1] + '.jpg'
        },
        {
            'title': 'Современные тренды веб-разработки',
            'text': '''Веб-разработка продолжает стремительно развиваться, принося новые технологии и подходы. 
            Давайте рассмотрим основные тренды, которые определяют современную веб-разработку.

            Progressive Web Apps (PWA) становятся всё более популярными. Они предоставляют пользователям возможность 
            работать с веб-приложениями так же удобно, как с нативными, включая работу офлайн и push-уведомления.

            Технология WebAssembly открывает новые горизонты производительности, позволяя запускать код, написанный на 
            C++ или Rust, прямо в браузере. Это особенно важно для ресурсоемких приложений, таких как игры или 
            инструменты для обработки медиа.

            Микрофронтенды позволяют разбивать большие приложения на независимые части, которые могут разрабатываться 
            и развертываться отдельно. Это упрощает поддержку крупных проектов и позволяет использовать разные 
            технологии для разных частей приложения.''',
            'author': 'Анна Черных',
            'date': fake.date_time_between(start_date='-2y', end_date='now'),
            'image_id': images_ids[2] + '.jpg'
        }
    ]
    post = posts_content[i % len(posts_content)]
    post['comments'] = generate_comments()  # Добавляем комментарии к посту
    return post

@lru_cache
def posts_list():
    return sorted([generate_post(i) for i in range(len(images_ids))], key=lambda p: p['date'], reverse=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list())

@app.route('/posts/<int:index>')
def post(index):
    try:
        p = posts_list()[index]
        return render_template('post.html', title=p['title'], post=p)
    except IndexError:
        abort(404)

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')
