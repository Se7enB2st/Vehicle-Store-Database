from flask import jsonify
import pymysql
import pandas as pd
import json

# MySQL 数据库连接配置
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'xil520'
DB_PASSWORD = 'Vehicle2710'
DB_NAME = 'vehiclestore_database'

def connect_db():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass = pymysql.cursors.DictCursor
        )
        print("连接成功！")
        return connection
    except pymysql.MySQLError as e:
        print(f"MySQL 错误: {e}")
        return None
    except Exception as e:
        print(f"连接失败: {e}")
        return None

def execute_sql_file(filename):
    db = connect_db()  # 连接到数据库
    cursor = db.cursor()  # 创建游标
    with open(filename, 'r') as file:  # 打开 SQL 文件
        sql_script = file.read()  # 读取 SQL 脚本
        for statement in sql_script.split(';'):  # 按照分号分割 SQL 语句
            if statement.strip():  # 如果语句不为空
                cursor.execute(statement)  # 执行 SQL 语句
    db.commit()  # 提交事务
    cursor.close()  # 关闭游标
    db.close()  # 关闭数据库连接
    
def check_login_api(username):
    try:
        db = connect_db()
        cursor = db.cursor()

        # 合并查询
        cursor.execute("""
                SELECT Password.password
                FROM User
                JOIN UserUsePassword ON User.user_id = UserUsePassword.user_id
                JOIN Password ON UserUsePassword.password_id = Password.password_id
                WHERE User.username = %s
            """, (username,))

        result = cursor.fetchone()
        print(f"Query result for username {username}: {result}")  # 调试输出
        password_result = result['password'] if result else None
        print(f"Password fetched: {password_result}")  # 输出密码值

    except pymysql.MySQLError as err:
        print(f"Database error: {err}")
        password_result = None

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    if password_result is None:
        return jsonify({'error': 'Invalid username or password'}), 400

    return jsonify({'password': password_result})

def register_api(username, password, confirm_password):
    # Check if the username already exists
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM User WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    cursor.close()
    db.close()

    if existing_user:
        error_message = "Username already exists. Please enter a different username."
        response = {'status': 'error', 'message': error_message}
        return jsonify(response)
    elif password != confirm_password:
        error_message = "The passwords entered twice are inconsistent."
        response = {'status': 'error', 'message': error_message}
        return jsonify(response)
    elif password == confirm_password:
        # Insert the new user into the database
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO User (username) VALUES (%s)", (username,))
            user_id = cursor.lastrowid
            # cursor.execute("INSERT INTO UserIsUserType (user_id, type_id) VALUES (%s, %s)",
            #                (user_id, 1 if user_type == 'tenant' else 2))
            cursor.execute("INSERT INTO Password (password) VALUES (%s)", (password,))
            password_id = cursor.lastrowid
            cursor.execute("INSERT INTO UserUsePassword (user_id, password_id) VALUES (%s, %s)",
                           (user_id, password_id))
            db.commit()
            cursor.close()
            db.close()
            response = {'status': 'success', 'message': 'Registration successful! You can now login.'}
            return jsonify(response)  # Return JSON response upon success

        except Exception as e:
            # Handle registration errors
            error_message = "Registration failed. Please try again."
            response = {'status': 'error', 'message': error_message}
            return jsonify(response)

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

                if vehicle_id and booking_date and user_id:
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

def get_seller_contracts_api(username):
    db = connect_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("""
            SELECT c.contract_id, c.signing_date, c.contract_price, 
                   vi.make, vi.model, vi.year
            FROM Contract c
            JOIN Vehicle v ON c.vehicle_id = v.vehicle_id
            JOIN VehicleInfo vi ON v.vehicle_id = vi.vehicle_id
            JOIN User u ON c.user_id = u.user_id
            WHERE u.username = %s
        """, (username,))
        contracts = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(contracts)
    except Exception as e:
        print(f"Error fetching contracts: {e}")
        return jsonify([])

def publish_vehicle_api(user_id, form_data):
    db = connect_db()
    cursor = db.cursor()
    try:
        # Get user_id
        cursor.execute("SELECT user_id FROM User WHERE username = %s", (username,))
        user_result = cursor.fetchone()
        if not user_result:
            return jsonify({'success': False, 'message': 'User not found'})
        user_id = user_result[0]

        # Insert into Vehicle table first
        cursor.execute("INSERT INTO Vehicle (user_id) VALUES (%s)", (user_id,))
        vehicle_id = cursor.lastrowid

        # Insert vehicle info
        cursor.execute("""
            INSERT INTO VehicleInfo 
            (vehicle_id, year, make, model, vin, color, listing_date, listing_price, status) 
            VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), %s, 'Available')
        """, (
            vehicle_id,
            form_data.get('Year', 0),
            form_data.get('Make', ''),
            form_data.get('Model', ''),
            form_data.get('Vin Number', ''),
            form_data.get('Color', ''),
            form_data.get('Listing Price', 0.0)
        ))

        db.commit()
        cursor.close()
        db.close()

        return jsonify({
            'success': True, 
            'message': 'Vehicle published successfully!'
        })
    
    except Exception as e:
        print(f"Error publishing vehicle: {e}")
        return jsonify({
            'success': False, 
            'message': 'Failed to publish vehicle. Please try again.'
        })

# Helper function to generate contracts HTML
def generate_contracts_html(contracts):
    if not contracts:
        return "<p>No contracts found.</p>"
    
    html = '<div class="contracts-listing">'
    for contract in contracts:
        html += f'''
        <div class="contract-item">
            <h4>{contract['make']} {contract['model']} ({contract['year']})</h4>
            <p>Contract ID: {contract['contract_id']}</p>
            <p>Signing Date: {contract['signing_date']}</p>
            <p>Price: ${contract['contract_price']:.2f}</p>
        </div>
        '''
    html += '</div>'
    return html
