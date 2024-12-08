SHOW TABLES LIKE 'VehicleInfo';

-- 删除旧视图（如果存在）
DROP VIEW IF EXISTS DetailedVehicleInfo;

-- 创建新的 VehicleInfo 替代视图
CREATE OR REPLACE VIEW DetailedVehicleInfo AS
SELECT 
    v.vehicle_id,
    vi.year AS year_made,
    vi.make AS brand,
    vi.model,
    vi.color,
    vi.listing_price,
    vi.status,
    a.street AS address_street,
    a.city AS address_city,
    a.state AS address_state,
    z.zipcode AS address_zipcode
FROM 
    Vehicle v
JOIN 
    VehicleInfo vi ON v.vehicle_id = vi.vehicle_id
LEFT JOIN 
    Address a ON v.vehicle_id = a.address_id -- 假设 Address 表直接与 Vehicle 表关联
LEFT JOIN 
    ZipCode z ON a.zipcode_id = z.zipcode_id;

-- 创建 UserVehicleInfo 视图
CREATE OR REPLACE VIEW UserVehicleInfo AS
SELECT 
    u.user_id,
    u.username,
    v.vehicle_id,
    vi.year AS year_made,
    vi.make AS brand,
    vi.model,
    vi.color,
    vi.listing_price,
    vi.status
FROM 
    User u
JOIN 
    Vehicle v ON u.user_id = v.user_id
JOIN 
    VehicleInfo vi ON v.vehicle_id = vi.vehicle_id;
-- 创建 VehicleMarketListings 视图
CREATE OR REPLACE VIEW VehicleMarketListings AS
SELECT 
    v.vehicle_id,
    vi.year AS year_made,
    vi.make AS brand,
    vi.model,
    vi.color,
    vi.listing_price,
    vi.status
FROM 
    Vehicle v
JOIN 
    VehicleInfo vi ON v.vehicle_id = vi.vehicle_id;

-- 创建 VehicleColorSummary 视图
CREATE OR REPLACE VIEW VehicleColorSummary AS
SELECT 
    color,
    COUNT(*) AS vehicle_count,
    MIN(listing_price) AS min_price,
    MAX(listing_price) AS max_price
FROM VehicleInfo
GROUP BY color;

-- 查询按最高价格降序排列
SELECT * FROM VehicleColorSummary ORDER BY max_price DESC;

