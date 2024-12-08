-- Indexes for primary key columns
CREATE INDEX idx_vehicle_id ON Vehicle (vehicle_id);
CREATE INDEX idx_user_id ON User (user_id);
CREATE INDEX idx_booking_id ON Booking (booking_id);
CREATE INDEX idx_contract_id ON Contract (contract_id);
CREATE INDEX idx_review_id ON Review (review_id);
CREATE INDEX idx_payment_id ON Payment (payment_id);
CREATE INDEX idx_payment_method_id ON PaymentMethod (payment_method_id);
CREATE INDEX idx_zipcode_id ON ZipCode (zipcode_id);
CREATE INDEX idx_address_id ON Address (address_id);

-- Indexes for foreign key columns used in JOINs
CREATE INDEX idx_fk_vehicle_id_contract ON Contract (vehicle_id);
CREATE INDEX idx_fk_user_id_review ON Review (user_id);
CREATE INDEX idx_fk_vehicle_id_review ON Review (vehicle_id);
CREATE INDEX idx_fk_user_id_booking ON Booking (user_id);
CREATE INDEX idx_fk_vehicle_id_booking ON Booking (vehicle_id);
CREATE INDEX idx_fk_contract_id_payment ON Payment (contract_id);
CREATE INDEX idx_fk_payment_method_id ON Payment (payment_method_id);
CREATE INDEX idx_fk_zipcode_id_address ON Address (zipcode_id);

-- Indexes for frequently used columns in WHERE clauses
CREATE INDEX idx_listing_date_vehicleinfo ON VehicleInfo (listing_date);
CREATE INDEX idx_listing_price_vehicleinfo ON VehicleInfo (listing_price);
CREATE INDEX idx_status_vehicleinfo ON VehicleInfo (status);
CREATE INDEX idx_start_date_booking ON Booking (start_date);
CREATE INDEX idx_end_date_booking ON Booking (end_date);
CREATE INDEX idx_payment_date ON Payment (payment_date);


-- for search
CREATE INDEX idx_color ON VehicleInfo(color);
CREATE INDEX idx_listing_price ON VehicleInfo(listing_price);

