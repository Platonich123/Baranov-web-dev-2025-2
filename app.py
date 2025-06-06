from flask import Flask, render_template, request, make_response, redirect, url_for
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/url_params')
def url_params():
    return render_template('url_params.html', params=request.args)

@app.route('/headers')
def headers():
    return render_template('headers.html', headers=dict(request.headers))

@app.route('/cookies')
def cookies():
    response = make_response(render_template('cookies.html', cookies=request.cookies))
    
    if 'user_id' not in request.cookies:
        response.set_cookie('user_id', '12345')
    else:
        response.delete_cookie('user_id')
    
    return response

@app.route('/form_params', methods=['GET', 'POST'])
def form_params():
    if request.method == 'POST':
        return render_template('form_params.html', form_data=request.form)
    return render_template('form_params.html')

@app.route('/phone', methods=['GET', 'POST'])
def phone():
    error = None
    formatted_number = None
    
    if request.method == 'POST':
        phone_number = request.form.get('phone', '')
        
        if not phone_number:
            error = 'Недопустимый ввод. Неверное количество цифр.'
        # Проверяем допустимые символы
        elif not re.match(r'^[\d\s()\-\.+]+$', phone_number):
            error = 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'
        else:
            # Удаляем все допустимые символы
            digits = re.sub(r'[^\d]', '', phone_number)
            
            # Проверяем количество цифр и формат
            if len(digits) == 11:
                if not (digits.startswith('7') or digits.startswith('8')):
                    error = 'Недопустимый ввод. Неверное количество цифр.'
                else:
                    digits = digits[1:]  # Убираем первую цифру
                    formatted_number = f"8-{digits[:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}"
            elif len(digits) == 10:
                formatted_number = f"8-{digits[:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}"
            else:
                error = 'Недопустимый ввод. Неверное количество цифр.'
    
    return render_template('phone.html', error=error, formatted_number=formatted_number)

if __name__ == '__main__':
    app.run(debug=True) 