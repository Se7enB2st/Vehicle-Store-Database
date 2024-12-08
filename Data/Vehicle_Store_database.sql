CREATE DATABASE vehiclestore_database;

USE vehiclestore_database;

-- Drop Tables if they already exist
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS Booking;

DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Contract;

DROP TABLE IF EXISTS VehicleInfo;
DROP TABLE IF EXISTS Vehicle;

DROP TABLE IF EXISTS UserUsePassword;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Password;

DROP TABLE IF EXISTS PaymentMethod;

-- User Table
CREATE TABLE User (
	user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE -- Ensure usernames are unique
) ENGINE=InnoDB;

CREATE TABLE Password (
    password_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE UserUsePassword (
    user_id INT UNIQUE,
    password_id INT,
    PRIMARY KEY (user_id, password_id),
    CONSTRAINT fk_user_id1 FOREIGN KEY (user_id) REFERENCES User(user_id),
    CONSTRAINT fk_password_id1 FOREIGN KEY (password_id) REFERENCES Password(password_id)
) ENGINE=InnoDB;

-- Vehicle Table
CREATE TABLE Vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE -- Cascade delete to clean up associated vehicles when a user is deleted
);

-- VehicleInfo Table
CREATE TABLE VehicleInfo (
    vehicleinfo_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    year INT NOT NULL CHECK (year >= 1886), -- Ensures year is valid (1886 is the year of the first car)
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    vin VARCHAR(17) NOT NULL UNIQUE, -- VIN should be unique
    color VARCHAR(50) NOT NULL,
    listing_date DATE NOT NULL,
    listing_price DECIMAL(10, 2) NOT NULL, -- Specify precision for decimals
    status VARCHAR(20) NOT NULL CHECK (status IN ('Available', 'Sold', 'Pending')), -- Limit valid status values
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE -- Ensure vehicle details are cleaned up if the vehicle is deleted
);

-- Review Table
CREATE TABLE Review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5), -- Rating should be between 1 and 5
    comments VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE, -- Cleanup reviews if user is deleted
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE -- Cleanup reviews if vehicle is deleted
);

-- Booking Table
CREATE TABLE Booking (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE, -- Cleanup bookings if user is deleted
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE -- Cleanup bookings if vehicle is deleted
);

-- Contract Table
CREATE TABLE Contract (
    contract_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    signing_date DATE NOT NULL,
    contract_price DECIMAL(10, 2) NOT NULL, -- Specify precision for decimals
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE, -- Cleanup contracts if user is deleted
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id) ON DELETE CASCADE -- Cleanup contracts if vehicle is deleted
);

-- PaymentMethod Table
CREATE TABLE PaymentMethod (
    payment_method_id INT AUTO_INCREMENT PRIMARY KEY,
    method VARCHAR(50) NOT NULL UNIQUE -- Payment method names should be unique
);

-- Payment Table
CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL, -- Specify precision for decimals
    payment_date DATE NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES Contract(contract_id) ON DELETE CASCADE, -- Cleanup payments if contract is deleted
    FOREIGN KEY (payment_method_id) REFERENCES PaymentMethod(payment_method_id)
);



-- 可按数量降序排列，也可以改为 ASC 实现升序
SELECT 
    color, 
    COUNT(*) AS vehicle_count
FROM VehicleInfo
GROUP BY color
ORDER BY vehicle_count DESC; 



-- 按颜色分类后，按价格降序排列
SELECT 
    color, 
    listing_price
FROM VehicleInfo
ORDER BY color ASC, listing_price DESC; 


-- 按平均价格降序排列
SELECT 
    color, 
    COUNT(*) AS vehicle_count,
    MIN(listing_price) AS min_price,
    MAX(listing_price) AS max_price,
    AVG(listing_price) AS avg_price
FROM VehicleInfo
GROUP BY color
ORDER BY avg_price DESC; 

