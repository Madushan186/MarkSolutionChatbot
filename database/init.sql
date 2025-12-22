CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(255),
    sale_date DATE NOT NULL,
    amount NUMERIC NOT NULL
);

-- Insert sample data (Mocking today's sync)
INSERT INTO sales (item_name, sale_date, amount) VALUES
('Initial_Seed_Data', CURRENT_DATE, 42500);
