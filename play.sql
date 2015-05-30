--INSERT INTO matches VALUES(DEFAULT,214,211);
--INSERT INTO matches VALUES(DEFAULT,213,212);

DELETE FROM matches WHERE id in (
    SELECT
        m_id
    FROM
        tournament_matches,matches
    WHERE
        t_id = 3);
--DELETE FROM tournament_matches WHERE t_id = 3;
