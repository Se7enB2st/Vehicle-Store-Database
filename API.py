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
                SELECT User.user_id, Password.password
                FROM User
                JOIN UserUsePassword ON User.user_id = UserUsePassword.user_id
                JOIN Password ON UserUsePassword.password_id = Password.password_id
                WHERE User.username = %s
            """, (username,))

        result = cursor.fetchone()
        print(f"Query result for username {username}: {result}")  # 调试输出

        if result:
            user_id = result.get('user_id')  # 使用 get 避免 KeyError
            password_result = result.get('password')  # 使用 get 避免 KeyError
            print(f"User ID: {user_id}, Password fetched: {password_result}")  # 输出用户ID和密码
        else:
            user_id = None
            password_result = None
            print(f"No user found for username {username}")




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

    return jsonify({'user_id': user_id, 'password': password_result})

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
            # response = {'status': 'success', 'message': 'Registration successful! You can now login.'}
            response = {'status': 'success', 'message': ''}
            return jsonify(response)  # Return JSON response upon success

        except Exception as e:
            # Handle registration errors
            error_message = "Registration failed. Please try again."
            response = {'status': 'error', 'message': error_message}
            return jsonify(response)




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

def get_available_vehicles_api():
    # Connect to the database
    db = connect_db()
    cursor = db.cursor()

    try:
        # Query for available vehicles
        query = "SELECT * FROM vehicles WHERE status = 'available'"
        cursor.execute(query)
        vehicles = cursor.fetchall()

        # If no vehicles are available
        if not vehicles:
            response = {'status': 'error', 'message': 'No available vehicles found.'}
            return jsonify(response)

        # Format the data for JSON response
        vehicle_list = []
        for vehicle in vehicles:
            vehicle_list.append({
                'id': vehicle['id'],
                'make': vehicle['make'],
                'model': vehicle['model'],
                'year': vehicle['year'],
                'price': vehicle['price'],
                'color': vehicle['color'],
                'status': vehicle['status']
            })

        # Return a success response with the list of vehicles
        response = {'status': 'success', 'vehicles': vehicle_list}
        return jsonify(response)

    except Exception as e:
        # Handle errors and return an error response
        error_message = "Failed to fetch available vehicles. Please try again later."
        response = {'status': 'error', 'message': error_message, 'error_detail': str(e)}
        return jsonify(response)

    finally:
        # Ensure the database connection is closed
        cursor.close()
        db.close()


def get_booking_data(vehicle_id):
    try:
        connection = connect_db()
        if connection:
            with connection.cursor() as cursor:
                # 查询车辆预定信息
                query = """
                    SELECT vehicle_id, user_id, booking_date
                    FROM bookings
                    WHERE vehicle_id = %s
                """
                cursor.execute(query, (vehicle_id,))
                result = cursor.fetchall()

                if result:
                    return {'status': 'success', 'data': result}
                else:
                    return {'status': 'error', 'message': 'No bookings found for this vehicle.'}
        else:
            return {'status': 'error', 'message': 'Database connection failed.'}
    except Exception as e:
        print(f"Error fetching booking data: {e}")
        return {'status': 'error', 'message': 'An error occurred while fetching data.'}


def book_vehicle(user_id, vehicle_id, start_date, end_date):
    try:
        # 连接数据库
        connection = connect_db()
        if connection:
            with connection.cursor() as cursor:
                # 检查车辆是否存在
                cursor.execute("SELECT vehicle_id FROM vehicle WHERE vehicle_id = %s", (vehicle_id,))
                vehicle_exists = cursor.fetchone()

                if not vehicle_exists:
                    return {'status': 'error', 'message': f"Vehicle with ID {vehicle_id} does not exist."}

                # 检查用户是否存在
                cursor.execute("SELECT user_id FROM User WHERE user_id = %s", (user_id,))
                user_exists = cursor.fetchone()

                if not user_exists:
                    return {'status': 'error', 'message': f"User with ID {user_id} does not exist."}

                # 插入车辆预定信息
                query = """
                    INSERT INTO Booking (user_id, vehicle_id, start_date, end_date)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (user_id, vehicle_id, start_date, end_date))
                connection.commit()  # 提交事务

                # return {'status': 'success', 'message': 'Booking successfully created!'}
                return {'status': 'success', 'message': ''}
        else:
            return {'status': 'error', 'message': 'Database connection failed.'}
    except Exception as e:
        print(f"Error processing booking: {e}")
        return {'status': 'error', 'message': 'An error occurred while booking the vehicle.'}

def insert_vehicle_data(user_id):
    """
    插入默认的 Vehicle 和 VehicleInfo 数据
    """
    try:
        db = connect_db()
        cursor = db.cursor()

        # 插入 Vehicle 数据
        cursor.execute("""
            INSERT INTO Vehicle (vehicle_id, user_id)
            VALUES 
            (1, %s),
            (2, %s),
            (3, %s)
        """, (user_id, user_id, user_id))

        # 插入 VehicleInfo 数据
        cursor.execute("""
            INSERT INTO VehicleInfo (vehicle_id, year, make, model, vin, color, listing_date, listing_price, status)
            VALUES 
            (1, 2022, 'Honda', 'Civic', '1HGCM82633A123456', 'White', '2024-12-01', 25999.00, 'Available'),
            (2, 2024, 'Toyota', 'Camry', '4T1BG22K8WU123456', 'White', '2024-12-02', 30000.00, 'Available'),
            (3, 2023, 'Ford', 'Mustang', '1FAFP4041WF123456', 'Red', '2024-12-03', 40000.00, 'Sold')
        """)

        db.commit()  # 提交事务
        cursor.close()
        db.close()
        return {'status': 'success', 'message': 'Vehicle data inserted successfully.'}
    except Exception as e:
        print(f"Error inserting vehicle data: {e}")
        return {'status': 'error', 'message': 'Failed to insert vehicle data.'}

def search_vehicles_api(query):
    try:
        db = connect_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        # 查询语句
        cursor.execute(
            "SELECT * FROM VehicleInfo WHERE make LIKE %s OR model LIKE %s OR CAST(year AS CHAR) LIKE %s",
            (query, query, query)
        )

        # 获取结果
        vehicles = cursor.fetchall()

        # 清理资源
        cursor.close()
        db.close()

        # 返回 JSON 格式数据
        return jsonify({'success': True, 'vehicles': vehicles})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


def sort_vehicles_api(query):
    try:
        db = connect_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        # 查询语句
        cursor.execute(
            "SELECT vehicle_id, year, make, model, vin, color, listing_date, listing_price, status FROM VehicleInfo WHERE make LIKE %s OR model LIKE %s ORDER BY listing_price DESC",
            (query, query)
        )

        # 获取结果
        vehicles = cursor.fetchall()

        # 清理资源
        cursor.close()
        db.close()

        # 返回 JSON 格式数据
        return jsonify({'success': True, 'vehicles': vehicles})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
