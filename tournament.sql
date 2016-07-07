-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE tournament;

CREATE DATABASE tournament;

\c tournament

 
CREATE TABLE players ( 
 	p_id serial PRIMARY KEY,
	p_name varchar(255)
 
);

CREATE TABLE tournaments ( 
	t_id serial PRIMARY KEY,
	t_name varchar(255) 
);

CREATE TABLE matches ( 
	m_id serial,
	t_id integer REFERENCES tournaments ON DELETE CASCADE,
	winner_id integer REFERENCES players(p_id) ON DELETE CASCADE,
	loser_id integer REFERENCES players(p_id) ON DELETE CASCADE,
	draw boolean,
	draw_id1 integer REFERENCES players(p_id) ON DELETE CASCADE,
	draw_id2 integer REFERENCES players(p_id) ON DELETE CASCADE
);

CREATE TABLE tregistrations ( 
	t_id integer REFERENCES tournaments ON DELETE CASCADE,
	p_id integer REFERENCES players ON DELETE CASCADE,
	bye integer 
);

-- intended columns: tournament id, player id, number of wins by that player
CREATE VIEW num_wins AS 
SELECT t.t_id, m.winner_id, m.count(winner_id) 
FROM tournaments AS t, matches AS m
WHERE t.t_id = m.t_id
GROUP BY m.winner_id
ORDER BY t.t_id, m.count(winner_id);

-- intended colums: tournament id, player id, number of draws by that player
CREATE VIEW num_draws AS
SELECT t.t_id, m.draw_id1, m.count(draw_id1)
FROM tournaments AS t, matches AS m
WHERE t.t_id = m.t_id
GROUP BY m.draw_id1
ORDER BY t.t_id, m.count(winner_id);

-- intended columns: tournament id, player id, number of wins, number of draws, number of byes, score
-- score is derived by the formula: 3 * number of wins + number of draws + 3 * no. of byes
CREATE VIEW derived_score AS
SELECT t.t_id, 
