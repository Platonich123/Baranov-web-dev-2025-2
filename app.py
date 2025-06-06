from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from whitenoise import WhiteNoise
from lab1.app import app as lab1_app
from lab2.app import app as lab2_app
from lab3.app import app as lab3_app
from root_app.app import app as root_app

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(root_app, {
    '/lab1': lab1_app,
    '/lab2': lab2_app,
    '/lab3': lab3_app
})

# Добавляем поддержку статических файлов через Whitenoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

application = app

if __name__ == "__main__":
    app.run();