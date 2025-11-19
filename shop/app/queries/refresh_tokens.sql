-- noinspection SqlInsertValuesForFile

-- name: get-refresh-tokens-by-user-id
SELECT id,
       user_id,
       token_hash,
       created_at,
       expires_at
FROM refresh_tokens
WHERE user_id = :user_id
ORDER BY created_at DESC;

-- name: get-refresh-token-by-hash^
SELECT id,
       user_id,
       token_hash,
       created_at,
       expires_at
FROM refresh_tokens
WHERE token_hash = :token_hash;

-- name: create-refresh-token^
INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
VALUES (:user_id, :token_hash, :expires_at)
RETURNING id;

-- name: delete-refresh-token^
DELETE FROM refresh_tokens
WHERE id = :id
RETURNING id;

-- name: delete-refresh-token-by-hash
DELETE FROM refresh_tokens
WHERE token_hash = :token_hash
RETURNING id;

-- name: delete-refresh-tokens-by-user-id
DELETE FROM refresh_tokens
WHERE user_id = :user_id
RETURNING id;

