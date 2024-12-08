DELIMITER $$

CREATE DEFINER=`pel131`@`%`
PROCEDURE `CreateContractAndPayment`(
    IN p_contract_price DECIMAL(10, 2),
    IN p_user_id INT,
    IN p_vehicle_id INT,
    IN p_payment_amount DECIMAL(10, 2),
    IN p_payment_method_id INT
)
BEGIN
    -- Declare variables for storing the IDs of the newly inserted contract and payment
    DECLARE v_contract_id INT;

    -- Error handling: declare an exit handler for SQL exceptions
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- Rollback the transaction if any SQL error occurs
        ROLLBACK;
        -- Optionally, re-raise an error to indicate failure
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error occurred during transaction. Rolling back.';
    END;

    -- Start a new transaction
    START TRANSACTION;

    -- Step 1: Insert a new contract record into the Contract table
    INSERT INTO Contract (signing_date, contract_price, user_id, vehicle_id)
    VALUES (CURRENT_DATE(), p_contract_price, p_user_id, p_vehicle_id);

    -- Step 2: Retrieve the ID of the newly inserted contract record
    SET v_contract_id = LAST_INSERT_ID();

    -- Step 3: Insert a new payment record into the Payment table
    INSERT INTO Payment (contract_id, payment_method_id, amount, payment_date)
    VALUES (v_contract_id, p_payment_method_id, p_payment_amount, CURRENT_DATE());

    -- Step 4: Commit the transaction
    COMMIT;
END$$

DELIMITER ;
