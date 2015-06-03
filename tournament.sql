-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Players.
CREATE TABLE player (
    id serial PRIMARY KEY,
    fullname text
);

-- Tournaments.
CREATE TABLE tournament (
    id serial PRIMARY KEY,
    name text
);

-- Matches played.
CREATE TABLE matches (
    id serial PRIMARY KEY,
    winner_id INT REFERENCES player (id),
    loser_id INT REFERENCES player (id)
);

-- Links a match to a tournament.
CREATE TABLE tournament_matches (
    t_id INT REFERENCES tournament (id),
    m_id INT REFERENCES matches (id) ON DELETE CASCADE
);

-- Players registered to play in a tournament.
CREATE TABLE tournament_players (
    t_id INT REFERENCES tournament (id),
    p_id INT REFERENCES player (id)
);

-- View of the winning players ordered by most won
CREATE VIEW winner_table AS
    SELECT
        winner_id,
        count(winner_id) AS wins
     FROM matches
     GROUP BY winner_id
     ORDER BY wins DESC;

-- View of the losing players ordered by most lost
CREATE VIEW loser_table AS
    SELECT
        loser_id,
        COUNT(loser_id) AS losts
     FROM matches
    GROUP BY loser_id
    ORDER BY losts DESC;
