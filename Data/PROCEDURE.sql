USE vehiclestore_database;
DELIMITER //

CREATE PROCEDURE GetVehicleInfoByColorAndPrice(
    IN sort_order_price VARCHAR(4) -- 'ASC' 或 'DESC'
)
BEGIN
    SET @query = CONCAT(
        'SELECT color, 
                COUNT(*) AS vehicle_count, 
                AVG(listing_price) AS avg_price 
         FROM VehicleInfo 
         GROUP BY color 
         ORDER BY avg_price ', sort_order_price);

    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //

DELIMITER ;
