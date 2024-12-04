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

def get_state_api():
    db = connect_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT DISTINCT state FROM Address")
        states = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(states)
    except Exception as e:
        print(f"Error fetching states: {e}")
        return jsonify([])

def get_city_api(state_name):
    db = connect_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT DISTINCT city FROM Address WHERE state = %s", (state_name,))
        cities = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(cities)
    except Exception as e:
        print(f"Error fetching cities for {state_name}: {e}")
        return jsonify([])

def schedule_appointment_api(username, vehicle_id, appointment_date):
    db = connect_db()
    cursor = db.cursor()
    try:
        # First, get the user_id from username
        cursor.execute("SELECT user_id FROM User WHERE username = %s", (username,))
        user_result = cursor.fetchone()
        
        if not user_result:
            return jsonify({'success': False, 'message': 'User not found'})
        
        user_id = user_result[0]
        
        # Insert booking
        cursor.execute("""
            INSERT INTO Booking 
            (user_id, vehicle_id, start_date, end_date) 
            VALUES (%s, %s, %s, %s)
        """, (user_id, vehicle_id, appointment_date, appointment_date))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'message': 'Booking scheduled successfully'})
    
    except Exception as e:
        print(f"Error scheduling booking: {e}")
        return jsonify({'success': False, 'message': 'Failed to schedule booking'})

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

def publish_vehicle_api(username, form_data):
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

        # Insert address
        cursor.execute("""
            INSERT INTO ZipCode (zipcode) VALUES (%s)
        """, (form_data.get('Zipcode', '00000'),))
        zipcode_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO Address (street, city, state, zipcode_id) 
            VALUES (%s, %s, %s, %s)
        """, (
            form_data.get('Address', ''),
            form_data.get('City', ''),
            form_data.get('State', ''),
            zipcode_id
        ))

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
