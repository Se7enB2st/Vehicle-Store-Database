-- Drop Tables if they already exist
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS Booking;
DROP TABLE IF EXISTS Contract;
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Vehicle;
DROP TABLE IF EXISTS VehicleInfo;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS PaymentMethod;

-- User Table
CREATE TABLE User (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Review Table
CREATE TABLE Review (
    review_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    rating INT NOT NULL,
    comments VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

-- Vehicle Table
CREATE TABLE Vehicle (
    vehicle_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

-- VehicleInfo Table
CREATE TABLE VehicleInfo (
    vehicleinfo_id INT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    year INT NOT NULL,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    vin VARCHAR(17) NOT NULL,
    color VARCHAR(50) NOT NULL,
    listing_date DATE NOT NULL,
    listing_price DECIMAL NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

-- Booking Table
CREATE TABLE Booking (
    booking_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

-- Contract Table
CREATE TABLE Contract (
    contract_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    signing_date DATE NOT NULL,
    contract_price DECIMAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

-- Payment Table
CREATE TABLE Payment (
    payment_id INT PRIMARY KEY,
    contract_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    amount DECIMAL NOT NULL,
    payment_date DATE NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES Contract(contract_id),
    FOREIGN KEY (payment_method_id) REFERENCES PaymentMethod(payment_method_id)
);

-- PaymentMethod Table
CREATE TABLE PaymentMethod (
    payment_method_id INT PRIMARY KEY,
    method VARCHAR(50) NOT NULL
);

