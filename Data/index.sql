-- Indexes for primary key columns
CREATE UNIQUE INDEX idx_vehicle_id ON Vehicle (vehicle_id); -- 主键索引
CREATE UNIQUE INDEX idx_user_id ON User (user_id);
CREATE UNIQUE INDEX idx_booking_id ON Booking (booking_id);
CREATE UNIQUE INDEX idx_contract_id ON Contract (contract_id);
CREATE UNIQUE INDEX idx_review_id ON Review (review_id);
CREATE UNIQUE INDEX idx_payment_id ON Payment (payment_id);
CREATE UNIQUE INDEX idx_payment_method_id ON PaymentMethod (payment_method_id);
CREATE UNIQUE INDEX idx_address_id ON Address (address_id); -- Address 表保留

-- Indexes for foreign key columns used in JOINs
CREATE INDEX idx_fk_vehicle_id_contract ON Contract (vehicle_id); -- Contract 表与 Vehicle 表关联
CREATE INDEX idx_fk_user_id_review ON Review (user_id);           -- Review 表与 User 表关联
CREATE INDEX idx_fk_vehicle_id_review ON Review (vehicle_id);     -- Review 表与 Vehicle 表关联
CREATE INDEX idx_fk_user_id_booking ON Booking (user_id);         -- Booking 表与 User 表关联
CREATE INDEX idx_fk_vehicle_id_booking ON Booking (vehicle_id);   -- Booking 表与 Vehicle 表关联
CREATE INDEX idx_fk_contract_id_payment ON Payment (contract_id); -- Payment 表与 Contract 表关联
CREATE INDEX idx_fk_payment_method_id ON Payment (payment_method_id); -- Payment 表与 PaymentMethod 表关联

-- Indexes for frequently used columns in WHERE clauses
CREATE INDEX idx_listing_date_vehicleinfo ON VehicleInfo (listing_date); -- 按 listing_date 查询优化
CREATE INDEX idx_listing_price_vehicleinfo ON VehicleInfo (listing_price); -- 按 listing_price 查询优化
CREATE INDEX idx_status_vehicleinfo ON VehicleInfo (status);             -- 按 status 查询优化
CREATE INDEX idx_start_date_booking ON Booking (start_date);             -- 按 start_date 查询优化
CREATE INDEX idx_end_date_booking ON Booking (end_date);                 -- 按 end_date 查询优化
CREATE INDEX idx_payment_date ON Payment (payment_date);                 -- 按 payment_date 查询优化

-- for search
CREATE INDEX idx_color ON VehicleInfo(color);                            -- 按 color 搜索优化
CREATE INDEX idx_listing_price ON VehicleInfo(listing_price);            -- 按 listing_price 搜索优化
