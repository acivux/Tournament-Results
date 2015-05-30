
INSERT INTO player VALUES(1,'a');
INSERT INTO player VALUES(2,'b');
INSERT INTO player VALUES(3,'c');
INSERT INTO player VALUES(4,'d');
INSERT INTO player VALUES(5,'e');
INSERT INTO matches VALUES(1,1,2);
INSERT INTO matches VALUES(2,3,4);
INSERT INTO matches VALUES(3,3,1);
INSERT INTO matches VALUES(4,2,4);
INSERT INTO matches VALUES(5,5,null);

-- INSERT INTO player VALUES(6,'f');

CREATE TEMP VIEW wintable AS
    SELECT
        winner_id,
        count(winner_id) AS wins
     FROM matches
     GROUP BY winner_id;

CREATE TEMP VIEW losertable AS
    SELECT loser_id,
        COUNT(loser_id) AS losts
    FROM matches
    GROUP BY loser_id;

SELECT
    player.id,
    player.fullname,
    COALESCE(wintable.wins,0) AS wins,
    COALESCE(wins,0) + COALESCE(losertable.losts, 0) AS matches
FROM
    player LEFT JOIN wintable
    ON player.id = wintable.winner_id
    LEFT JOIN losertable
    ON player.id = losertable.loser_id
ORDER BY wins DESC NULLS LAST;

SELECT DISTINCT
    winner_id,
    loser_id
FROM
    matches
WHERE
    loser_id is not null;


--DELETE FROM matches CASCADE;
--DELETE FROM player;
--DROP VIEW wintable;
--DROP VIEW losertable