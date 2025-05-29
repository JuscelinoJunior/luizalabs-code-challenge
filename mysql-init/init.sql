CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100),
    hashed_password VARCHAR(100) NOT NULL,
    role VARCHAR(50) DEFAULT 'customer'
);

CREATE TABLE IF NOT EXISTS wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    UNIQUE (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES `user`(id) ON DELETE CASCADE
);

-- Initial admin user
INSERT INTO user (email, name, hashed_password, role) VALUES
('admin@luizalabs.com', 'Admin User', '$2b$12$nEcFXmOyEFUVwxHqbpXu2uQz5kM9HnlDHsX4PEy3mgIhe0P/3F7Du', 'admin')
ON DUPLICATE KEY UPDATE email=email;