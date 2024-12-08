

USE vehiclestore_database;



-- 可按数量降序排列，也可以改为 ASC 实现升序
SELECT 
    color, 
    COUNT(*) AS vehicle_count
FROM VehicleInfo
GROUP BY color
ORDER BY vehicle_count DESC; 



-- 按车辆上市价格降序排列
SELECT 
    vehicle_id, 
    year, 
    make, 
    model, 
    vin, 
    color, 
    listing_date, 
    listing_price, 
    status
FROM VehicleInfo
ORDER BY listing_price DESC;


