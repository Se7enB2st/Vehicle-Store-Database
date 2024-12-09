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

# Buyer Dashboard Fetch all available vehicles
def get_available_vehicles_api():
    db = connect_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        # Query to fetch all vehicles with status 'available'
        cursor.execute("SELECT * FROM Vehicle WHERE status = 'available'")
        vehicles = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify({'success': True, 'vehicles': vehicles})
    except Exception as e:
        print(f"Error fetching available vehicles: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch vehicles'})

# Buyer Dashboard - Book a vehicle
def book_vehicle_api(user_id, vehicle_id, start_date, end_date):
    db = connect_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    cursor = db.cursor()
    try:
        # Validate user existence
        cursor.execute("SELECT user_id FROM User WHERE user_id = %s", (user_id,))
        user_result = cursor.fetchone()
        if not user_result:
            return jsonify({'success': False, 'message': 'User not found'})

        # Validate vehicle existence
        cursor.execute("SELECT vehicle_id FROM Vehicle WHERE vehicle_id = %s AND status = 'available'", (vehicle_id,))
        vehicle_result = cursor.fetchone()
        if not vehicle_result:
            return jsonify({'success': False, 'message': 'Vehicle not available or does not exist'})

        # Check if the vehicle is already booked during the specified period
        cursor.execute("""
            SELECT * FROM Booking 
            WHERE vehicle_id = %s AND 
                  (start_date BETWEEN %s AND %s OR end_date BETWEEN %s AND %s)
        """, (vehicle_id, start_date, end_date, start_date, end_date))
        existing_booking = cursor.fetchone()

        if existing_booking:
            return jsonify({'success': False, 'message': 'Vehicle already booked during the selected period'})

        # Insert new booking
        cursor.execute("""
            INSERT INTO Booking (user_id, vehicle_id, start_date, end_date) 
            VALUES (%s, %s, %s, %s)
        """, (user_id, vehicle_id, start_date, end_date))

        # Fetch the newly created booking_id
        booking_id = cursor.lastrowid
        db.commit()
        cursor.close()
        db.close()

        return jsonify({'success': True, 'message': 'Booking created successfully', 'booking_id': booking_id})
    except Exception as e:
        db.rollback()
        print(f"Error creating booking: {e}")
        return jsonify({'success': False, 'message': 'Failed to create booking'})

# Helper to fetch a single vehicle's details
def get_vehicle_details_api(vehicle_id):
    db = connect_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        # Query to fetch vehicle details by ID
        cursor.execute("SELECT * FROM vehicles WHERE id = %s", (vehicle_id,))
        vehicle = cursor.fetchone()
        cursor.close()
        db.close()
        if vehicle:
            return jsonify({'success': True, 'vehicle': vehicle})
        else:
            return jsonify({'success': False, 'message': 'Vehicle not found'})
    except Exception as e:
        print(f"Error fetching vehicle details: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch vehicle details'})

#Seller Dashboard
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

# search bar
def search_vehicles_api(query):
    db = connect_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM VehicleInfo WHERE make LIKE %s OR model LIKE %s OR year LIKE %s", (query, query, query))
    vehicles = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(vehicles)
