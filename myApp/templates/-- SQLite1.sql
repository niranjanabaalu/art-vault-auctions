-- SQLite
DELETE FROM myApp_painting
WHERE id = (SELECT id FROM myApp_painting ORDER BY id DESC LIMIT 1);
