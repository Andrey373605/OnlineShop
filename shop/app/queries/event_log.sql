-- noinspection SqlInsertValuesForFile

-- name: get-all-event-log
SELECT id,
       event_type,
       user_id,
       description,
       ip_address,
       user_agent,
       created_at
FROM event_log
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset;

-- name: get-event-log-by-id^
SELECT id,
       event_type,
       user_id,
       description,
       ip_address,
       user_agent,
       created_at
FROM event_log
WHERE id = :id;

-- name: get-events-by-user-id
SELECT id,
       event_type,
       user_id,
       description,
       ip_address,
       user_agent,
       created_at
FROM event_log
WHERE user_id = :user_id
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset;

-- name: create-event-log^
INSERT INTO event_log (event_type,
                       user_id,
                       description,
                       ip_address,
                       user_agent)
VALUES (:event_type,
        :user_id,
        :description,
        :ip_address,
        :user_agent)
RETURNING id;

-- name: delete-event-log^
DELETE FROM event_log
WHERE id = :id
RETURNING id;

