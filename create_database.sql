CREATE DATABASE ecommerce_scraper_db;
CREATE USER es_user_admin WITH PASSWORD 'pwd_admin';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_scraper_db TO es_user_admin;
ALTER DATABASE ecommerce_scraper_db OWNER TO es_user_admin;