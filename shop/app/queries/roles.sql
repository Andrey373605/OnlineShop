-- noinspection SqlInsertValuesForFile

-- name: get-all-roles
SELECT id,
       name
FROM roles
ORDER BY id;

-- name: get-role-by-id^
SELECT id,
       name
FROM roles
WHERE id = :id;

-- name: get-role-by-name^
SELECT id,
       name
FROM roles
WHERE name = :name;

-- name: create-role^
INSERT INTO roles (name)
VALUES (:name)
RETURNING id;

-- name: update-role^
UPDATE roles
SET name = :name
WHERE id = :id
RETURNING id, name;

-- name: delete-role^
DELETE FROM roles
WHERE id = :id
RETURNING id;

-- name: check-role-name-exists^
SELECT EXISTS(SELECT 1 FROM roles WHERE name = :name) AS exists;

