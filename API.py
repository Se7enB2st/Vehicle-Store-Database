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
            database=DB_NAME
        )
        print("连接成功！")
        return connection
    except Exception as e:
        print(f"连接失败: {e}")
        return None

def check_login_api(username):
    # Perform a database query here to verify username and password match
    db = connect_db()
    cursor = db.cursor()

    # First query the User table for user_id
    cursor.execute("SELECT user_id FROM User WHERE username = %s", (username,))
    user_result = cursor.fetchone()
    if user_result:
        user_id = user_result[0]

        # Then query the related table to get the password_id
        cursor.execute("SELECT password_id FROM UserUsePassword WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if result:
            password_id = result[0]
            # Query plaintext passwords using password_id
            cursor.execute("SELECT password FROM Password WHERE password_id = %s", (password_id,))
            password_result = cursor.fetchone()[0]
            cursor.close()
            db.close()

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
