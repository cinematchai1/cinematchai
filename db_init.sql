CREATE DATABASE cinematch_db;
CREATE USER cinematch_user WITH PASSWORD 'cinematch_pass';
ALTER DATABASE cinematch_db OWNER TO cinematch_user;
\c cinematch_db
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);
ALTER TABLE users OWNER TO cinematch_user;
