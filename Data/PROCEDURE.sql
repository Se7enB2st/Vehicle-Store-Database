USE vehiclestore_database;
DELIMITER //

CREATE PROCEDURE GetVehicleInfoByColorAndPrice(
    IN sort_order_price ENUM('ASC', 'DESC') -- 确保只接受 'ASC' 或 'DESC'
)
BEGIN
    -- 验证输入参数是否为有效值
    IF sort_order_price NOT IN ('ASC', 'DESC') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid sort order. Use "ASC" or "DESC".';
    ELSE
        -- 构建动态查询语句
        SET @query = CONCAT(
            'SELECT color, 
                    COUNT(*) AS vehicle_count
             FROM VehicleInfo 
             GROUP BY color 
             ORDER BY vehicle_count ', sort_order_price);

        -- 准备并执行动态查询
        PREPARE stmt FROM @query;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //

DELIMITER ;
