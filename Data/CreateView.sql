CREATE VIEW UserVehicleInfo AS
SELECT 
    u.user_id,
    u.f_name,
    u.l_name,
    v.vehicle_id,
    v.description,
    vi.year_made,
    vi.model,
    vi.brand,
    vi.color
FROM 
    User u
JOIN 
    Vehicle v ON u.user_id = v.vehicle_id
JOIN 
    Vehicleinfo vi ON v.vehicle_id = vi.vehicle_id;
CREATE VIEW VehicleMarketListings AS
SELECT 
    v.vehicle_id,
    v.description,
    ml.listing_id,
    ml.listing_date,
    ml.listing_price,
    ml.status
FROM 
    Vehicle v
JOIN 
    MarketListings ml ON v.vehicle_id = ml.vehicle_id;

DROP VIEW IF EXISTS VehicleInfo;
CREATE VIEW VehicleInfo AS
SELECT v.vehicle_id, v.description, year_made, brand, model, color, c.city_name FROM Vehicle v
JOIN VehicleLocateAddress vla ON v.vehicle_id = vla.fk_vehicle_id
JOIN Address a ON vla.fk_address_id = a.address_id
JOIN AddressLocateCity alc ON a.address_id = alc.fk_address_id
JOIN City c ON alc.fk_city_id = c.city_id
JOIN Vehicleinfo vi ON v.vehicle_id = vi.vehicle_id;