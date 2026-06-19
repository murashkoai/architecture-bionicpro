DROP TABLE IF EXISTS users;

CREATE TABLE
    users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(200) NOT NULL,
        email VARCHAR(200) NOT NULL UNIQUE,
        device_id VARCHAR(50) NOT NULL
    );

INSERT INTO
    users (
        full_name,
        email,
        device_id
    )
VALUES
    ('user1', 'user1@example.com', '1001'),
    ('user2', 'user2@example.com', '1002');