from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
from captcha import generate_captcha_image
import io

from API import (check_login_api, register_api, execute_sql_file, get_seller_contracts_api,
                 publish_vehicle_api, generate_contracts_html, get_available_vehicles_api, book_vehicle,
                 insert_vehicle_data, search_vehicles_api, sort_vehicles_api)

app = Flask(__name__, template_folder="templates")
app.secret_key = "a_really_strong_and_unique_secret_key"

initialized = False  # 全局变量

@app.before_request
def initialize_db():
    global initialized  # 使用全局变量
    if not initialized:
        print("Initializing the database tables...")
        # 执行数据库初始化代码
        execute_sql_file('Data/Vehicle_Store_database.sql')
        initialized = True

@app.route("/", methods=['GET'])
def home():
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
            # 调用 check_login_api 获取响应对象
            response = check_login_api(username)

            # 获取响应对象的 JSON 数据
            response_data = response.get_json()

            if 'password' in response_data and 'user_id' in response_data:
                password_result = response_data['password']
                # 从 API 数据中获取 user_id

                if password_result and password_result == password:
                    session['logged_in'] = True
                    session['username'] = username
                    session['user_id'] = response_data['user_id']  # 正确存储 user_id
                    print(f"User logged in with ID: {response_data['user_id']}")  # 确认打印 user_id

                    # 调用插入数据的 API 函数
                    vehicle_response = insert_vehicle_data(response_data['user_id'])
                    if vehicle_response['status'] == 'error':
                        flash(vehicle_response['message'], 'error')
                        return render_template('login.html', error_message=vehicle_response['message'])

                    return redirect('/')  # 登录成功后跳转
            else:
                error_message = 'Invalid username or password'
                print(f"Session Data after login: {session}")
                return render_template('login.html', error_message=error_message)
        else:
            error_message = 'Invalid captcha'
            return render_template('login.html', error_message=error_message)

@app.route("/vehicle_details/<int:car_id>")
def vehicle_details(car_id):
    # 根据 car_id 来获取车辆的详细信息（这里只是举例）
    # 这里可以从数据库中获取相关信息
    vehicle_info = {
        1: {"make": "Honda", "model": "Civic", "year": "2022", "color": "White", "price": "$25,999", "status": "Available"},
        2: {"make": "Honda", "model": "Camry", "year": "2024", "color": "White", "price": "$30,000", "status": "Available"},
        3: {"make": "Ford", "model": "Mustang", "year": "2023", "color": "Red", "price": "$40,000", "status": "Sold"}
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


#Buyer Dashboard
@app.route('/book_vehicle', methods=['GET', 'POST'])
def book_vehicle_page():
    if request.method == 'GET':
        return render_template('book_vehicle.html', success=False)  # 用于展示预定页面
    elif request.method == 'POST':
        # 获取会话中的 user_id
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User is not logged in.'})

        # 获取表单数据
        vehicle_id = request.form.get('vehicle_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # 确保所有必填字段都存在
        if not all([vehicle_id, start_date, end_date]):
            flash('Vehicle ID, Start Date, and End Date are required!', 'error')
            return render_template('book_vehicle.html', success=False)

        # 调用 book_vehicle 函数进行预定
        responses = book_vehicle(user_id, vehicle_id, start_date, end_date)

        # 处理返回结果
        if responses['status'] == 'success':
            flash(responses['message'], 'success')
            return render_template('book_success.html', success=True)
            # return redirect('/')  # 预定成功后跳转到主页或其他页面
        else:
            flash(responses['message'], 'error')
            return render_template('book_vehicle.html', error_message=responses['message'])

@app.route('/search_vehicles', methods=['POST'])
def search_vehicles():
    data = request.get_json()  # 获取前端发送的 JSON 数据
    query = data.get('query', '').strip()  # 获取查询参数

    if not query:
        return jsonify({'success': False, 'message': 'No search query provided'})
    return search_vehicles_api(f"%{query}%")

@app.route('/sort', methods=['POST'])
def sort_vehicles():
    data = request.get_json()  # 获取前端发送的 JSON 数据
    query = data.get('query', '').strip()  # 获取查询参数

    if not query:
        return jsonify({'success': False, 'message': 'No search query provided'})
    return sort_vehicles_api(f"%{query}%")




if __name__ == '__main__':
    app.run(debug=True)

