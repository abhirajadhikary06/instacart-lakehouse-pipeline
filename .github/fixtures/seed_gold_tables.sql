-- Minimal fixture data for CI dbt tests.
-- Creates the gold tables that dbt staging models read from.

CREATE TABLE IF NOT EXISTS gold_product_popularity (
    product_id       INT,
    product_name     TEXT,
    department_id    INT,
    department       TEXT,
    times_ordered    BIGINT,
    times_reordered  BIGINT,
    reorder_rate     FLOAT
);

INSERT INTO gold_product_popularity VALUES
    (1, 'Organic Banana',     7,  'produce',      50000, 42000, 0.84),
    (2, 'Strawberries',       7,  'produce',      30000, 24000, 0.80),
    (3, 'Whole Milk',         16, 'dairy eggs',   45000, 38000, 0.84),
    (4, 'Sparkling Water',    7,  'beverages',    20000, 12000, 0.60),
    (5, 'Chicken Breast',     12, 'meat seafood', 15000, 11000, 0.73);

CREATE TABLE IF NOT EXISTS gold_department_summary (
    department_id    INT,
    department       TEXT,
    total_orders     BIGINT,
    reorder_rate     FLOAT
);

INSERT INTO gold_department_summary VALUES
    (7,  'produce',      120000, 0.82),
    (16, 'dairy eggs',    90000, 0.78),
    (12, 'meat seafood',  60000, 0.70),
    (1,  'snacks',        55000, 0.65);

CREATE TABLE IF NOT EXISTS gold_order_time_analysis (
    order_dow        INT,
    order_hour_of_day INT,
    total_orders     BIGINT,
    avg_basket_size  FLOAT
);

INSERT INTO gold_order_time_analysis VALUES
    (0, 10, 15000, 9.5),
    (0, 11, 18000, 9.8),
    (1, 10, 14000, 9.2),
    (2, 14, 12000, 8.9),
    (6, 20,  8000, 7.5);

CREATE TABLE IF NOT EXISTS gold_aisle_reorder_analysis (
    aisle_id     INT,
    aisle        TEXT,
    total_orders BIGINT,
    reorder_rate FLOAT
);

INSERT INTO gold_aisle_reorder_analysis VALUES
    (24, 'fresh fruits',       80000, 0.85),
    (83, 'milk',               70000, 0.80),
    (123,'fresh vegetables',   75000, 0.82),
    (31, 'refrigerated',       40000, 0.68);

CREATE TABLE IF NOT EXISTS gold_user_order_behaviour (
    user_id                   INT,
    total_orders              INT,
    total_products_ordered    INT,
    avg_add_to_cart_position  FLOAT,
    max_days_since_prior_order FLOAT,
    unique_products_count     INT,
    avg_basket_size           FLOAT,
    avg_days_between_orders   FLOAT
);

INSERT INTO gold_user_order_behaviour VALUES
    (1,  12, 150, 5.2, 30.0, 80,  12.5, 8.3),
    (2,   3,  20, 3.1, 14.0, 18,   6.7, 10.0),
    (3,   7,  80, 7.8, 21.0, 55,  11.4, 7.5),
    (4,   1,   8, 2.5,  null, 8,   8.0, null),
    (5,  20, 300, 9.0, 10.0, 200, 15.0, 6.0);
