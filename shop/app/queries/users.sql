-- noinspection SqlInsertValuesForFile

-- name: get-all-users
SELECT u.id,
       u.username,
       u.email,
       u.full_name,
       u.is_active,
       u.role       AS role_id,
       r.name       AS role_name,
       u.last_login,
       u.created_at,
       u.updated_at
FROM users u
LEFT JOIN roles r ON u.role = r.id
ORDER BY u.id
LIMIT :limit OFFSET :offset;

-- name: get-users-count
SELECT COUNT(*) AS total
FROM users;

-- name: get-user-by-id^
SELECT u.id,
       u.username,
       u.email,
       u.full_name,
       u.is_active,
       u.role       AS role_id,
       r.name       AS role_name,
       u.last_login,
       u.created_at,
       u.updated_at
FROM users u
LEFT JOIN roles r ON u.role = r.id
WHERE u.id = :id;

-- name: get-user-by-username^
SELECT u.id,
       u.username,
       u.email,
       u.full_name,
       u.is_active,
       u.role       AS role_id,
       r.name       AS role_name,
       u.last_login,
       u.created_at,
       u.updated_at,
       u.password_hash
FROM users u
LEFT JOIN roles r ON u.role = r.id
WHERE u.username = :username;

-- name: create-user^
INSERT INTO users (username,
                   email,
                   password_hash,
                   full_name,
                   is_active,
                   role,
                   last_login)
VALUES (:username,
        :email,
        :password_hash,
        :full_name,
        COALESCE(:is_active, TRUE),
        :role,
        :last_login)
RETURNING id;

-- name: update-user^
UPDATE users
SET username      = COALESCE(:username, username),
    email         = COALESCE(:email, email),
    password_hash = COALESCE(:password_hash, password_hash),
    full_name     = COALESCE(:full_name, full_name),
    is_active     = COALESCE(:is_active, is_active),
    role          = COALESCE(:role, role),
    last_login    = COALESCE(:last_login, last_login),
    updated_at    = NOW()
WHERE id = :id
RETURNING id;

-- name: delete-user^
DELETE FROM users
WHERE id = :id
RETURNING id;

-- name: check-user-username-exists^
SELECT EXISTS(SELECT 1 FROM users WHERE username = :username) AS exists;

-- name: check-user-email-exists^
SELECT EXISTS(SELECT 1 FROM users WHERE email = :email) AS exists;
