CREATE VIEW UserVehicleInfo AS
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
CREATE VIEW VehicleMarketListings AS
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
DROP VIEW IF EXISTS VehicleInfo;

CREATE VIEW VehicleInfo AS
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
JOIN 
    Address a ON v.vehicle_id = a.address_id -- Assuming Address is linked directly to vehicles
JOIN 
    ZipCode z ON a.zipcode_id = z.zipcode_id;
