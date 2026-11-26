DROP DATABASE IF EXISTS techno_sphere;
CREATE DATABASE techno_sphere CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE techno_sphere;

CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    login VARCHAR(50) NOT NULL UNIQUE,
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE categories (
    cat_id INT AUTO_INCREMENT PRIMARY KEY,
    cat_name VARCHAR(100) NOT NULL
);

CREATE TABLE subcategories (
    subcat_id INT AUTO_INCREMENT PRIMARY KEY,
    cat_id INT NOT NULL,
    subcat_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (cat_id) REFERENCES categories(cat_id)
);

CREATE TABLE products (
    prod_id INT AUTO_INCREMENT PRIMARY KEY,
    subcat_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(100),
    descr TEXT,
    specs TEXT,
    price DECIMAL(10,2) NOT NULL,
    img VARCHAR(255),
    FOREIGN KEY (subcat_id) REFERENCES subcategories(subcat_id)
);

CREATE TABLE modifications (
    mod_id INT AUTO_INCREMENT PRIMARY KEY,
    mod_name VARCHAR(100) NOT NULL
);

CREATE TABLE stock (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    prod_id INT NOT NULL,
    mod_id INT NOT NULL,
    qty INT NOT NULL DEFAULT 0,
    FOREIGN KEY (prod_id) REFERENCES products(prod_id),
    FOREIGN KEY (mod_id) REFERENCES modifications(mod_id)
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    dt DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    stock_id INT NOT NULL,
    qty INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (stock_id) REFERENCES stock(stock_id)
);