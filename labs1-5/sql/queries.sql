-- queries.sql
-- 5 SELECT
SELECT * FROM Requests;
SELECT full_name, role FROM Users;
SELECT theme, created_date FROM Requests WHERE status_id = 1;
SELECT name FROM Categories ORDER BY name DESC;
SELECT text, author_id FROM Comments WHERE request_id = 2;

-- 3 SELECT с WHERE
SELECT * FROM Users WHERE role = 'Исполнитель';
SELECT * FROM Requests WHERE category_id = 1 AND status_id = 1;
SELECT * FROM Requests WHERE created_date > '2026-10-02';

-- 2 JOIN
SELECT r.reg_number, r.theme, s.name AS status, c.name AS category 
FROM Requests r
JOIN Statuses s ON r.status_id = s.id 
JOIN Categories c ON r.category_id = c.id;

SELECT u.full_name, r.theme 
FROM Requests r
JOIN Users u ON r.executor_id = u.id;

-- 2 UPDATE
UPDATE Requests SET status_id = 2, executor_id = 3 WHERE id = 1;
UPDATE Comments SET text = 'Обновлено: Стул привезут завтра' WHERE id = 1;

-- 2 DELETE
DELETE FROM Comments WHERE id = 2;
DELETE FROM Requests WHERE id = 5;
