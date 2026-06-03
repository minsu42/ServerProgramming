CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    excluded_barbecue_restaurant BOOLEAN,
    excluded_american_restaurant BOOLEAN,
    excluded_bakery BOOLEAN,
    excluded_brazilian_restaurant BOOLEAN,
    excluded_chinese_restaurant BOOLEAN,
    excluded_fast_food_restaurant BOOLEAN,
    excluded_italian_restaurant BOOLEAN,
    excluded_japanese_restaurant BOOLEAN,
    excluded_korean_restaurant BOOLEAN,
    excluded_pizza_restaurant BOOLEAN,
    excluded_sandwich_shop BOOLEAN,
    excluded_vietnamese_restaurant BOOLEAN
);
