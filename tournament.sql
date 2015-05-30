-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE player (
    id serial PRIMARY KEY,
    fullname text
);

CREATE TABLE tournament (
    id serial PRIMARY KEY,
    name text
);

CREATE TABLE matches (
    id serial PRIMARY KEY,
    winner_id INT REFERENCES player (id),
    loser_id INT REFERENCES player (id)
);

CREATE TABLE tournament_matches (
    t_id INT REFERENCES tournament (id),
    m_id INT REFERENCES matches (id) ON DELETE CASCADE
);

CREATE TABLE tournament_players (
    t_id INT REFERENCES tournament (id),
    p_id INT REFERENCES player (id)
);
