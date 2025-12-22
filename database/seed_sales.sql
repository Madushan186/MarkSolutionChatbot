TRUNCATE TABLE sales;
BEGIN;
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_January', 950000, '2025-01-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_February', 800000, '2025-02-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_March', 1100000, '2025-03-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_April', 900000, '2025-04-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_May', 1200000, '2025-05-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_June', 1050000, '2025-06-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_July', 1150000, '2025-07-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_August', 980000, '2025-08-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_September', 1100000, '2025-09-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_October', 900000, '2025-10-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_November', 950000, '2025-11-01');
INSERT INTO sales (item_name, amount, sale_date) VALUES ('API_Monthly_Sync_December', 1420000, '2025-12-01'),
('API_day_Sync', 45000, CURRENT_DATE),
('API_yesterday_Sync', 42100, CURRENT_DATE - INTERVAL '1 day');
COMMIT;