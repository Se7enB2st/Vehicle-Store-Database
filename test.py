from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
from captcha import generate_captcha_image
import io

from API import (check_login_api,
                  register_api, execute_sql_file, get_seller_contracts_api, publish_vehicle_api, generate_contracts_html)

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
            # 调用 check_login_api 获取响应对象
            response = check_login_api(username)

            # 获取响应对象的 JSON 数据
            response_data = response.get_json()

            if 'password' in response_data:
                password_result = response_data['password']
                if password_result and password_result == password:
                    session['logged_in'] = True
                    session['username'] = username
                    return redirect('/')  # 登录成功后跳转
            else:
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

#Buyer Dashboard
@app.route('/dashboard_buyer', methods=['GET', 'POST'])
def buyer_dashboard():
    if not session.get('logged_in'):
        flash('Please log in to access the dashboard', 'error')
        return redirect(url_for('login'))

    try:
        if request.method == 'GET':
            # Fetch all available vehicles from the database
            connection = connect_db()
            if connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM vehicles WHERE status = 'available'"  # Ensure only available vehicles are shown
                    cursor.execute(query)
                    vehicles = cursor.fetchall()

                # Render the vehicles as HTML
                html_data_vehicle = ""
                for vehicle in vehicles:
                    html_data_vehicle += f"""
                        <div class="vehicle-card">
                            <h3>{vehicle['make']} {vehicle['model']}</h3>
                            <p>Year: {vehicle['year']}</p>
                            <p>Price: ${vehicle['price']}</p>
                            <p>Color: {vehicle['color']}</p>
                            <button class="booking-button" data-vehicle-id="{vehicle['id']}">
                                Book Now
                            </button>
                        </div>
                    """

                return render_template('dashboard_buyer.html', html_data_vehicle=html_data_vehicle)
            else:
                flash('Database connection failed', 'error')
                return render_template('dashboard_buyer.html')

        elif request.method == 'POST':
            action = request.form.get('action')

            if action == 'book_vehicle':
                vehicle_id = request.form.get('vehicle_id')
                booking_date = request.form.get('booking_date')
                user_id = session.get('user_id')  # Use username from session

                if vehicle_id and booking_date and username:
                    connection = connect_db()
                    if connection:
                        with connection.cursor() as cursor:
                            # Insert the booking into the database
                            query = """
                                INSERT INTO bookings (vehicle_id, user_id, booking_date)
                                VALUES (%s, %s, %s)
                            """
                            cursor.execute(query, (vehicle_id, user_id, booking_date))
                            connection.commit()

                        return jsonify({'success': True, 'message': 'Booking successfully created!'})
                    else:
                        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
                else:
                    return jsonify({'success': False, 'message': 'Incomplete form data.'})

            return jsonify({'success': False, 'message': 'Invalid action.'})

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'})

#Seller Dashboard        
@app.route('/dashboard_seller', methods=['GET', 'POST'])
def seller_dashboard():
    if not session.get('logged_in'):
        flash('Please log in to access the dashboard', 'error')
        return redirect(url_for('login'))

    username = session.get('username')
    
    if request.method == 'GET':
        # Fetch contracts for the seller
        contracts = get_seller_contracts_api(username).json
        
        # Generate HTML for contracts
        html_data_contracts = generate_contracts_html(contracts)
        
        return render_template('dashboard_seller.html', html_data_contracts=html_data_contracts)
    
    elif request.method == 'POST':
        # Handle vehicle publishing
        return publish_vehicle_api(username, request.form)

if __name__ == '__main__':
    app.run(debug=True)
