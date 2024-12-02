-- Creating indexes based on application usage

-- Indexes for primary key columns
CREATE INDEX idx_id_vehicle ON Vehicle (vehicle_id);
CREATE INDEX idx_id_user ON User (user_id);
CREATE INDEX idx_id_booking ON Bookings (booking_id);
CREATE INDEX idx_id_contract ON Contract (contract_id);
CREATE INDEX idx_id_review ON Review (review_id);

-- Indexes for foreign key columns used in JOINs
CREATE INDEX idx_fk_vehicle_id_contract ON Contract (fk_vehicle_id);
CREATE INDEX idx_fk_user_id_review ON Review (fk_user_id);
CREATE INDEX idx_fk_vehicle_id_review ON Review (fk_vehicle_id);

-- Indexes for frequently used columns in WHERE clauses
CREATE INDEX idx_booking_time ON Bookings (booking_time);
CREATE INDEX idx_contract_id ON Contract (contract_id);
