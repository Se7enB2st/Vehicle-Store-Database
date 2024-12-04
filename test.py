from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
from captcha import generate_captcha_image
import io

from API import (check_login_api,
                  register_api, )

app = Flask(__name__, template_folder="templates")
app.secret_key = "a_really_strong_and_unique_secret_key"

@app.route("/")
def car_display():
    return render_template('car_display.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')  # 显示登录页面
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        captcha = request.form['captcha']


        if captcha.upper() == session.get('captcha', '').upper():
           password_result = check_login_api(username).json['password']
           if password_result and password_result == password:
               session['logged_in'] = True
               session['username'] = username  # or session['user_id'] = user_id depending on how you manage the session
           error_message = 'Invalid username or password'
           return render_template('login.html', error_message=error_message)
        else:
           error_message = 'Invalid captcha'
           return render_template('login.html', error_message=error_message)

@app.route("/vehicle_details/<int:car_id>")
def vehicle_details(car_id):
    # 根据 car_id 来获取车辆的详细信息（这里只是举例）
    # 这里可以从数据库中获取相关信息
    vehicle_info = {
        1: {"make": "Honda", "model": "Civic", "year": "2025", "color": "Red", "price": "$25,999", "status": "Available"},
        2: {"make": "Toyota", "model": "Camry", "year": "2024", "color": "Blue", "price": "$30,000", "status": "Available"},
        3: {"make": "Ford", "model": "Mustang", "year": "2023", "color": "Black", "price": "$40,000", "status": "Sold"}
    }
    # 获取对应 car_id 的车辆信息
    vehicle = vehicle_info.get(car_id)
    return render_template('vehicle_details.html', vehicle=vehicle)

@app.route('/captcha')
def captcha():
    # Generate a CAPTCHA image using the above function
    image, captcha_text = generate_captcha_image()

    # Store CAPTCHA text to session for later validation
    session['captcha'] = captcha_text

    buf = io.BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue(), 200, {
        'Content-Type': 'image/png',
        'Content-Length': str(len(buf.getvalue()))
    }
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        # Get user input from the registration form
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        # user_type = request.form['user_type']  # Get the selected user type
        # Add more fields as needed

        responses = register_api(username, password, confirm_password).json
        if responses['status'] == 'success':
            flash(responses['message'], 'success')  # Flash a success message
            return redirect('/')
        elif responses['status'] == 'error':
            return render_template('register.html', error_message=responses['message'])

@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'GET':
        return render_template('User.html')
    elif request.method == 'POST':
        return render_template('User.html')


if __name__ == '__main__':
    app.run(debug=True)
