
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(50),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(10) NOT NULL DEFAULT 'user', -- Возможные значения: 'user', 'admin'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    type VARCHAR(50),
    material VARCHAR(50),
    price NUMERIC(10,2) NOT NULL,
    image_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Триггер для обновления поля updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE favorites (
    favorite_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id INT NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE (user_id, product_id)
);

CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('new_product', 'discount', 'promotion')),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE chats (
    chat_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    manager_id BIGINT,
    message TEXT NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (manager_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индекс на email в таблице users
CREATE INDEX idx_users_email ON users(email);

-- Индекс на name в таблице products
CREATE INDEX idx_products_name ON products(name);

-- Индексы на user_id и product_id в таблице favorites
CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_favorites_product_id ON favorites(product_id);

-- Индекс на user_id в таблице notifications
CREATE INDEX idx_notifications_user_id ON notifications(user_id);

-- Индекс на user_id и manager_id в таблице chats
CREATE INDEX idx_chats_user_id ON chats(user_id);
CREATE INDEX idx_chats_manager_id ON chats(manager_id);

-- Индекс на user_id в таблице logs
CREATE INDEX idx_logs_user_id ON logs(user_id);
